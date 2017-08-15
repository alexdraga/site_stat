from django.core.management import BaseCommand
from os import path, rename

from reports.models import GrabberLog

from django.conf import settings


NEW_EXTENSION = ".txt"


class Command(BaseCommand):
    def handle(self, *args, **options):
        renamed = 0
        not_affected = 0
        for grab in GrabberLog.objects.all():
            grab_filename = grab.filename.name
            actual_filename = path.join(settings.GRABS_DIR, grab_filename)
            if path.exists(actual_filename) and path.isfile(actual_filename):
                new_actual_filename = self.change_extension_actual(actual_filename, NEW_EXTENSION)
                new_filename = self.change_extension_base(grab_filename, NEW_EXTENSION)
                if actual_filename != new_filename:
                    rename(actual_filename, new_actual_filename)
                    grab.filename = new_filename
                    grab.save()
                    renamed += 1
                else:
                    not_affected += 1

        print "Renamed %s records to %s extension, not affected: %s" % (renamed, NEW_EXTENSION, not_affected)

    def change_extension_actual(self, filename, extension):
        filepath, fileextension = path.splitext(filename)
        if len(fileextension):
            return filepath + extension
        else:
            return filepath

    def change_extension_base(self, grab_filename, extension):
        filepath, fileextension = path.splitext(grab_filename)
        if len(fileextension):
            return filepath + extension
        else:
            return filepath
