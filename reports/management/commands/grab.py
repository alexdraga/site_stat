# coding: utf-8
import codecs
from os import path, makedirs
from time import sleep

import requests
from django.utils import timezone
from django.core.management import BaseCommand
from requests import RequestException

from input_data.models import Site
from reports.models import GrabberLog
from django.conf import settings


class Command(BaseCommand):
    def handle(self, *args, **options):
        while True:
            self.grab_sites()
            sleep(settings.GRAB_SLEEP_TIMEOUT)

    def grab_sites(self):
        results = []
        sites = [x for x in Site.objects.all()]
        for site in sites:
            response = self.get_site_page(site)
            if response is not None:
                results.append(response)
        if results:
            GrabberLog.objects.bulk_create(results)

    def get_site_page(self, site):
        try:
            response = requests.session().get(site.url)
            if response.status_code == 200:
                grab_log = GrabberLog(site=site, created_at=timezone.now())
                grab_log.filename = self.get_grab_filename(site.name, grab_log.created_at)
                actual_filename = path.join(settings.GRABS_DIR, grab_log.filename.name)
                with codecs.open(actual_filename, 'w', "utf8") as f:
                    f.write(response.text)
                return grab_log
        except RequestException:
            pass

    def get_grab_filename(self, site_name, created_at):
        _dir = "%s_%s_%s" % (created_at.day, created_at.month, created_at.year)
        cur_log_dir = path.join(_dir, site_name)
        actual_log_dir = path.join(settings.GRABS_DIR, cur_log_dir)
        if not path.exists(actual_log_dir):
            makedirs(actual_log_dir)
        created_at_str = created_at.strftime("%d_%m_%Y_%H_%M_%S_%f")
        return path.join(cur_log_dir,
                         "%s_%s.html" % (site_name, created_at_str))
