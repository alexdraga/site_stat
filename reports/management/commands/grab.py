# coding: utf-8
import codecs
import os
from os import path
from time import sleep

import requests
from django.utils import timezone
from django.core.management import BaseCommand

from settings.models import Site
from reports.models import GrabberLog
from site_stat.settings import GRAB_DIR, GRAB_SLEEP_TIMEOUT


class Command(BaseCommand):
    def handle(self, *args, **options):
        while True:
            self.grab_sites()
            sleep(GRAB_SLEEP_TIMEOUT)

    @classmethod
    def grab_sites(cls):
        results = []
        sites = [x for x in Site.objects.all()]
        for site in sites:
            response = Command.get_site_page(site)
            if response is not None:
                results.append(response)
        if len(results):
            GrabberLog.objects.bulk_create(results)

    @classmethod
    def get_site_page(cls, site):
        response = requests.session().get(site.url)
        if response.status_code == 200:
            grab_log = GrabberLog(site=site, created_at=timezone.now())
            grab_log.filename = Command.grab_filename(site.name, grab_log.created_at)
            with codecs.open(grab_log.filename.name, 'w', "utf8") as f:
                f.write(response.text)
            return grab_log

    @classmethod
    def grab_filename(cls, site_name, created_at):
        year = str(created_at.year)
        month = str(created_at.month)
        day = str(created_at.day)
        subdir = "%s_%s_%s" % (day, month, year)
        cur_log_dir = path.join(GRAB_DIR,
                                subdir,
                                site_name)
        if not os.path.exists(cur_log_dir):
            os.makedirs(cur_log_dir)
        created_at_str = str(created_at).replace('-', '_').replace(':', '_').\
            replace('.', '_').replace('+', '_')
        return path.join(
            cur_log_dir,
            "%s_%s.html" % (site_name, created_at_str))
