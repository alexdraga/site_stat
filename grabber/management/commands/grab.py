# coding: utf-8
import io
from os import path

import requests
from django.core.management import BaseCommand

from grabber.models import Site, GrabberLog


class Command(BaseCommand):

    def handle(self, *args, **options):
        results = []
        for site in Site.objects:
            response = self.get_site_page(site)
            if response is not None:
                results.append(response)
        if len(results):
            GrabberLog.objects.bulk_create(results)

    def get_site_page(self, site):
        response = requests.session().get(site.url)
        if response.status_code == 200:
            grab_log = GrabberLog(site=site)
            filename = path.join(path.dirname(__file__), "%s_%s.html" % (site.name, grab_log.created_at))
            grab_log.filename = filename
            with io.open(filename, 'w') as f:
                f.write(response.text)
            return grab_log
