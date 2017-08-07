import codecs
from collections import OrderedDict
from time import sleep

import xlsxwriter
from django.core.management import BaseCommand
from os import path

from reports.models import ReportRequest, GrabberLog
from django.conf import settings


class Command(BaseCommand):
    def handle(self, *args, **options):
        while True:
            self.process_reports()
            sleep(settings.REPORT_SLEEP_TIMEOUT)

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
                    site=site).order_by('created_at')
                found_templates = self.search_templates(files, templates)
                if found_templates:
                    report[site.name] = found_templates

            if len(report):
                request.status = ReportRequest.Statuses.FINISHED
                report_filename = self.get_report_filename(request.id,
                                                           sites)
                self.write_xls_report(report_filename, report)
                request.filename = report_filename
            else:
                request.status = ReportRequest.Statuses.ERROR
            request.save()

    def search_templates(self, files, templates):
        report = OrderedDict()
        if len(files):
            for f in files:
                day = f.created_at.date()
                report.setdefault(day, {})
                for template in templates:
                    report[day].setdefault(template.name, 0)
                    if path.exists(f.filename.name):
                        with codecs.open(f.filename.name, 'r', "utf8") as f:
                            if f.read().find(template.template) != -1:
                                report[day][template.name] += 1
        return report

    def get_report_filename(self, request_id, sites):
        filename = "%s_%s.xlsx" % (request_id,
                                   '_'.join([s.name for s in sites]))
        return path.join(settings.REPORT_DIR, filename)

    def write_xls_report(self, filename, report):
        workbook = xlsxwriter.Workbook(filename)

        title_format = workbook.add_format({'bold': True, 'font_size': 16})
        template_name_format = workbook.add_format({'bold': True})
        date_format = workbook.add_format({'num_format': 'dd/mm/yyyy'})

        for site, data in report.iteritems():
            worksheet = workbook.add_worksheet(site)
            title = "Report for %s" % site
            max_column_sizes = {0: 25}
            worksheet.write(0, 0, title, title_format)

            current_row = 2
            templates_row = 1
            templates_columns = {}
            max_template_column = 1
            for date, templates in data.iteritems():
                worksheet.write_datetime(current_row, 0, date, date_format)
                for template, template_number in templates.iteritems():
                    if template not in templates_columns:
                        templates_columns[template] = max_template_column
                        worksheet.write(templates_row, max_template_column, template, template_name_format)
                        max_column_sizes.setdefault(max_template_column, len(template))
                        max_template_column += 1
                    worksheet.write(current_row, templates_columns[template], template_number)
                    if len(str(template_number)) > max_column_sizes[templates_columns[template]]:
                        max_column_sizes[templates_columns[template]] = len(str(template_number))
                current_row += 1

            for column, size in max_column_sizes.iteritems():
                worksheet.set_column(column, column, size)

        workbook.close()
