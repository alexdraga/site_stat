from datetime import timedelta
from time import sleep
from zipfile import ZipFile, ZIP_DEFLATED

from django.core.management import BaseCommand
from os import path, chdir

from reports.models import GrabberLog, ZipRequest
from django.conf import settings
from django.utils import timezone

from workers.models import Worker


class Command(BaseCommand):
    def handle(self, *args, **options):
        worker = Worker.objects.filter(worker_name=Worker.WorkerNames.ZIP)
        now = timezone.now()
        if not len(worker):
            Worker.objects.create(worker_name=Worker.WorkerNames.ZIP,
                                  timeout=settings.ZIP_SLEEP_TIMEOUT,
                                  next_run=now,
                                  heartbeat=now)

        while True:
            worker = Worker.objects.filter(worker_name=Worker.WorkerNames.ZIP)[0]
            now = timezone.now()
            if now > worker.next_run:
                worker.next_run = now + timedelta(seconds=worker.timeout)
                self.process_zips()
            worker.heartbeat = timezone.now() + timedelta(seconds=settings.WORKER_CHECK_TIMEOUT * 2)
            worker.save(update_fields=["heartbeat", "next_run"])
            sleep(settings.WORKER_CHECK_TIMEOUT)

    def process_zips(self):
        unprocessed_requests = ZipRequest.objects.filter(status=ZipRequest.Statuses.IN_PROGRESS)
        zip_requests = [z for z in unprocessed_requests]
        for zip_request in zip_requests:
            sites = zip_request.sites.all()
            archive_files = GrabberLog.objects.filter(
                created_at__range=[zip_request.starts_from,
                                   zip_request.ends_from],
                site__in=sites)
            filenames = [path.join(settings.GRABS_DIR,
                                   f.filename.name) for f in archive_files if f.filename is not None]
            if len(filenames):
                zip_filename = self.get_zip_filename(zip_request.id, sites)
                actual_filename = path.join(settings.ZIPS_DIR, zip_filename)
                if self.perform_zip(actual_filename, filenames):
                    zip_request.filename = zip_filename
                    zip_request.status = ZipRequest.Statuses.FINISHED
                else:
                    zip_request.status = ZipRequest.Statuses.ERROR
                if zip_request.delete_sources:
                    archive_files.delete()
            else:
                zip_request.status = ZipRequest.Statuses.NO_DATA
            zip_request.save()

    def get_zip_filename(self, request_id, sites):
        filename = "%s_%s.zip" % (request_id,
                                  '_'.join([s.name for s in sites]),)
        return filename

    def perform_zip(self, destination, sources):
        archived = False
        with ZipFile(destination, 'w', ZIP_DEFLATED) as myzip:
            chdir(settings.GRABS_DIR)
            for filename in sources:
                rel_filename = '.' + filename.split(settings.GRABS_DIR)[1]
                if path.exists(rel_filename):
                    myzip.write(rel_filename)
                    archived = True
        myzip.close()
        return archived
