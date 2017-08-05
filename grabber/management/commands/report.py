from time import sleep

from django.core.management import BaseCommand


class Command(BaseCommand):

    def handle(self, *args, **options):
        while True:
            print 1
            sleep(1)