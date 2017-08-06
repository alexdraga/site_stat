# coding: utf-8
import codecs
from os import path
from time import sleep

import requests
from datetime import datetime
from django.core.management import BaseCommand

from grabber.models import Site, GrabberLog
from site_stat.settings import GRAB_DIR


class Command(BaseCommand):

    def handle(self, *args, **options):
        while True:
            self.grab_sites()
            sleep(1)

    def created_at_to_filename(self, created_at):
        return str(created_at).replace('-', '_').replace(':', '_').replace('.', '_').replace('+', '_')

    def grab_sites(self):
        results = []
        sites = [x for x in Site.objects.all()]
        for site in sites:
            response = self.get_site_page(site)
            if response is not None:
                results.append(response)
        if len(results):
            GrabberLog.objects.bulk_create(results)

    def get_site_page(self, site):
        response = requests.session().get(site.url)
        if response.status_code == 200:
            grab_log = GrabberLog(site=site, created_at=datetime.utcnow())
            filename = path.join(GRAB_DIR,
                                 "%s_%s.html" % (site.name,
                                                 self.created_at_to_filename(grab_log.created_at)))
            grab_log.filename = filename
            with codecs.open(filename, 'w', "utf8") as f:
                f.write(response.text)
            return grab_log
