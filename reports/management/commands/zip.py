import os
from time import sleep
from zipfile import ZipFile

from django.core.management import BaseCommand

from reports.models import GrabberLog, ZipRequest
from site_stat.settings import ZIPS_DIR, ZIP_SLEEP_TIMEOUT, GRAB_DIR


class Command(BaseCommand):
    def handle(self, *args, **options):
        while True:
            self.process_zips()
            sleep(ZIP_SLEEP_TIMEOUT)

    def process_zips(self):
        unprocessed_requests = ZipRequest.objects.filter(status=ZipRequest.Statuses.IN_PROGRESS)
        zip_requests = [z for z in unprocessed_requests]
        for zip_request in zip_requests:
            sites = zip_request.sites.all()
            archive_files = GrabberLog.objects.filter(
                created_at__range=[zip_request.starts_from,
                                   zip_request.ends_from],
                site__in=sites)
            filenames = [f.filename.name for f in archive_files if f.filename is not None]
            if len(filenames):
                zip_filename = self.zip_filename(zip_request.id, sites)
                self.perform_zip(zip_filename, filenames)
                zip_request.filename = zip_filename
                zip_request.status = ZipRequest.Statuses.FINISHED
            else:
                zip_request.status = ZipRequest.Statuses.ERROR
            zip_request.save()

    def zip_filename(self, request_id, sites):
        filename = "%s_%s.zip" % (request_id,
                                  '_'.join([s.name for s in sites]),)
        return os.path.join(ZIPS_DIR, filename)

    def perform_zip(self, destination, sources):
        with ZipFile(destination, 'w') as myzip:
            os.chdir(GRAB_DIR)
            for filename in sources:
                rel_filename = '.' + filename.split(GRAB_DIR)[1]
                myzip.write(rel_filename)
        myzip.close()

    def created_at_to_filename(self, created_at):
        return str(created_at).replace('-', '_').replace(':', '_').replace('.', '_').replace('+', '_')
