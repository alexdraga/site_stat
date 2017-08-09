from time import sleep
from zipfile import ZipFile

from django.core.management import BaseCommand
from os import path, chdir

from reports.models import GrabberLog, ZipRequest
from django.conf import settings


class Command(BaseCommand):
    def handle(self, *args, **options):
        while True:
            self.process_zips()
            sleep(settings.ZIP_SLEEP_TIMEOUT)

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
                self.perform_zip(actual_filename, filenames)
                zip_request.filename = zip_filename
                zip_request.status = ZipRequest.Statuses.FINISHED
            else:
                zip_request.status = ZipRequest.Statuses.ERROR
            zip_request.save()

    def get_zip_filename(self, request_id, sites):
        filename = "%s_%s.zip" % (request_id,
                                  '_'.join([s.name for s in sites]),)
        return filename

    def perform_zip(self, destination, sources):
        with ZipFile(destination, 'w') as myzip:
            chdir(settings.GRABS_DIR)
            for filename in sources:
                rel_filename = '.' + filename.split(settings.GRABS_DIR)[1]
                myzip.write(rel_filename)
        myzip.close()
