from django.core.management import BaseCommand
from os import path, rename

from reports.models import GrabberLog

from site_stat.settings import GRABS_DIR


NEW_EXTENSION = ".txt"


class Command(BaseCommand):
    def handle(self, *args, **options):
        renamed = 0
        not_affected = 0
        for grab in GrabberLog.objects.all():
            grab_filename = grab.filename.name
            actual_filename = path.join(GRABS_DIR, grab_filename)
            if path.exists(actual_filename) and path.isfile(actual_filename):
                new_filename = self.change_extension(actual_filename, NEW_EXTENSION)
                if actual_filename != new_filename:
                    rename(actual_filename, new_filename)
                    grab.filename = new_filename
                    grab.save()
                    renamed += 1
                else:
                    not_affected += 1

        print "Renamed %s records to %s extension, not affected: %s" % (renamed, NEW_EXTENSION, not_affected)

    def change_extension(self, filename, extension):
        filepath, fileextension = path.splitext(filename)
        if len(fileextension):
            return filepath + extension
        else:
            return filepath
