import codecs
import json
import os
from time import sleep

from django.core.management import BaseCommand

from reports.models import ReportRequest, GrabberLog
from site_stat.settings import REPORT_DIR, REPORT_SLEEP_TIMEOUT


class Command(BaseCommand):
    def handle(self, *args, **options):
        while True:
            self.process_reports()
            sleep(REPORT_SLEEP_TIMEOUT)

    def process_reports(self):
        unprocessed_requests = ReportRequest.objects.filter(status=ReportRequest.Statuses.IN_PROGRESS)
        report_requests = [z for z in unprocessed_requests]
        for request in report_requests:
            sites = request.sites.all()
            templates = request.templates.all()
            report = {}
            for site in sites:
                files = GrabberLog.objects.filter(
                    created_at__range=[request.starts_from,
                                       request.ends_from],
                    site=site)
                report.setdefault(site.name, self.search_templates(files, templates))

            if not (len(report)):
                request.status = ReportRequest.Statuses.ERROR
            else:
                request.status = ReportRequest.Statuses.FINISHED
            report_filename = self.report_filename(request.id,
                                                   sites)
            self.write_report(report_filename, report)
            request.filename = report_filename
            request.save()

    def search_templates(self, files, templates):
        report = {}
        if len(files):
            for f in files:
                day = f.created_at.strftime("%d-%m-%Y")
                report.setdefault(day, {})
                for template in templates:
                    report[day].setdefault(template.name, 0)
                    if os.path.exists(f.filename.name):
                        with codecs.open(f.filename.name, 'r', "utf8") as f:
                            if f.read().find(template.template) != -1:
                                report[day][template.name] += 1
        return report

    def report_filename(self, request_id, sites):
        filename = "%s_%s.txt" % (request_id,
                                  '_'.join([s.name for s in sites]))
        return os.path.join(REPORT_DIR, filename)

    def write_report(self, filename, report):
        with codecs.open(filename, 'w', "utf8") as f:
            f.write(json.dumps(report))
        f.close()
