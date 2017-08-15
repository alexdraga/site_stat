import codecs
from collections import OrderedDict
from datetime import timedelta
from time import sleep

import xlsxwriter
from django.core.management import BaseCommand
from os import path

from reports.models import ReportRequest, GrabberLog
from django.conf import settings
from django.utils import timezone

from workers.models import Worker


class Command(BaseCommand):
    def handle(self, *args, **options):
        worker = Worker.objects.filter(worker_name=Worker.WorkerNames.REPORT)
        now = timezone.now()
        if not len(worker):
            Worker.objects.create(worker_name=Worker.WorkerNames.REPORT,
                                  timeout=settings.REPORT_SLEEP_TIMEOUT,
                                  next_run=now,
                                  heartbeat=now)

        while True:
            worker = Worker.objects.filter(worker_name=Worker.WorkerNames.REPORT)[0]
            now = timezone.now()
            if now > worker.next_run:
                worker.next_run = now + timedelta(seconds=worker.timeout)
                self.process_reports()
            worker.heartbeat = timezone.now() + timedelta(seconds=settings.WORKER_CHECK_TIMEOUT * 2)
            worker.save(update_fields=["heartbeat", "next_run"])
            sleep(settings.WORKER_CHECK_TIMEOUT)

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
                if request.detalisation == ReportRequest.Detalisation.DAY:
                    found_templates = self.search_templates_day(files, templates)
                elif request.detalisation == ReportRequest.Detalisation.HOUR:
                    found_templates = self.search_templates_hour(files, templates)
                elif request.detalisation == ReportRequest.Detalisation.FULL:
                    found_templates = self.search_templates_full(files, templates)
                else:
                    found_templates = {}

                if found_templates:
                    report[site.name] = found_templates

            if len(report):
                request.status = ReportRequest.Statuses.FINISHED
                report_filename = self.get_report_filename(request.id,
                                                           sites,
                                                           request.detalisation)
                actual_filename = path.join(settings.REPORTS_DIR, report_filename)
                if request.detalisation == ReportRequest.Detalisation.DAY:
                    self.write_xls_report_day(actual_filename, report)
                elif request.detalisation == ReportRequest.Detalisation.HOUR:
                    self.write_xls_report_hour(actual_filename, report)
                elif request.detalisation == ReportRequest.Detalisation.FULL:
                    self.write_xls_report_full(actual_filename, report)
                request.filename = report_filename
            else:
                request.status = ReportRequest.Statuses.NO_DATA
            request.save()

    def search_templates_day(self, files, templates):
        report = OrderedDict()
        if len(files):
            for f in files:
                day = f.created_at.date()
                report.setdefault(day, {})
                for template in templates:
                    report[day].setdefault(template.name, 0)
                    actual_filename = path.join(settings.GRABS_DIR, f.filename.name)
                    if path.exists(actual_filename):
                        with codecs.open(actual_filename, 'r', "utf8") as grab_file:
                            if grab_file.read().find(template.template) != -1:
                                report[day][template.name] += 1
        return report

    def search_templates_hour(self, files, templates):
        report = OrderedDict()
        if len(files):
            for f in files:
                day = f.created_at.date()
                hour = f.created_at.hour
                report.setdefault(day, OrderedDict()).setdefault('%sh' % hour, {})
                for template in templates:
                    report[day]['%sh' % hour].setdefault(template.name, 0)
                    actual_filename = path.join(settings.GRABS_DIR, f.filename.name)
                    if path.exists(actual_filename):
                        with codecs.open(actual_filename, 'r', "utf8") as grab_file:
                            if grab_file.read().find(template.template) != -1:
                                report[day]['%sh' % hour][template.name] += 1
        return report

    def search_templates_full(self, files, templates):
        report = OrderedDict()
        if len(files):
            for f in files:
                day = f.created_at.date()
                report.setdefault(day, OrderedDict())
                for template in templates:
                    report[day].setdefault(template.name, [])
                    filename = f.filename.name
                    actual_filename = path.join(settings.GRABS_DIR, filename)
                    if path.exists(actual_filename):
                        with codecs.open(actual_filename, 'r', "utf8") as grab_file:
                            if grab_file.read().find(template.template) != -1:
                                timestamp = f.created_at.strftime("%H:%M:%S")
                                report[day][template.name].append(timestamp)
        return report

    def get_report_filename(self, request_id, sites, detalisation):
        append = ""
        if detalisation == ReportRequest.Detalisation.DAY:
            append = "day"
        elif detalisation == ReportRequest.Detalisation.HOUR:
            append = "hour"
        elif detalisation == ReportRequest.Detalisation.FULL:
            append = "full"
        filename = "%s_%s_%s.xlsx" % (request_id,
                                      '_'.join([s.name for s in sites]),
                                      append)
        return filename

    def write_xls_report_day(self, filename, report):
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
                # Write day
                worksheet.write_datetime(current_row, 0, date, date_format)
                for template, template_number in templates.iteritems():
                    if template not in templates_columns:
                        templates_columns[template] = max_template_column
                        # Write template caption
                        worksheet.write(templates_row, max_template_column, template, template_name_format)
                        max_column_sizes.setdefault(max_template_column, len(template))
                        max_template_column += 1
                    # Write statistics
                    worksheet.write(current_row, templates_columns[template], template_number)
                    if len(str(template_number)) > max_column_sizes[templates_columns[template]]:
                        max_column_sizes[templates_columns[template]] = len(str(template_number))
                current_row += 1

            for column, size in max_column_sizes.iteritems():
                worksheet.set_column(column, column, size)

        workbook.close()

    def write_xls_report_hour(self, filename, report):
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
            max_template_column = 2
            for date, hour_templates in data.iteritems():
                # Write day
                worksheet.write_datetime(current_row, 0, date, date_format)
                current_row += 1
                for hour, templates in hour_templates.iteritems():
                    # Write hour
                    worksheet.write_string(current_row, 1, hour)
                    for template, template_number in templates.iteritems():
                        if template not in templates_columns:
                            templates_columns[template] = max_template_column
                            # Write template caption
                            worksheet.write(templates_row, max_template_column, template, template_name_format)
                            max_column_sizes.setdefault(max_template_column, len(template))
                            max_template_column += 1
                        # Write statistics
                        worksheet.write(current_row, templates_columns[template], template_number)
                        if len(str(template_number)) > max_column_sizes[templates_columns[template]]:
                            max_column_sizes[templates_columns[template]] = len(str(template_number))
                    current_row += 1

            for column, size in max_column_sizes.iteritems():
                worksheet.set_column(column, column, size)

        workbook.close()

    def write_xls_report_full(self, filename, report):
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
                # Write day
                worksheet.write_datetime(current_row, 0, date, date_format)
                current_row += 1
                max_row = current_row
                for template, occurencies in templates.iteritems():
                    started_row = current_row
                    if template not in templates_columns:
                        templates_columns[template] = max_template_column
                        # Write template caption
                        worksheet.write(templates_row, max_template_column, template, template_name_format)
                        max_column_sizes.setdefault(max_template_column, len(template))
                        max_template_column += 1
                    # Write statistics
                    for occurency in occurencies:
                        worksheet.write(started_row, templates_columns[template], occurency)
                        if len(str(occurency)) > max_column_sizes[templates_columns[template]]:
                            max_column_sizes[templates_columns[template]] = len(str(occurency))
                        started_row += 1
                    max_row = max(started_row, max_row)
                current_row = max_row + 1

            for column, size in max_column_sizes.iteritems():
                worksheet.set_column(column, column, size)

        workbook.close()
