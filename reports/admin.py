# -*- coding: utf-8 -*-
from __future__ import unicode_literals


from daterange_filter.filter import DateRangeFilter
from django.conf import settings
from django.contrib import admin
from django.db.models.signals import pre_delete
from os import path, remove

from django.utils.html import format_html

from reports.models import GrabberLog, ReportRequest, ZipRequest


def delete_file(sender, instance, **kwargs):
    if isinstance(instance, GrabberLog):
        _dir = settings.GRABS_DIR
    elif isinstance(instance, ReportRequest):
        _dir = settings.REPORTS_DIR
    elif isinstance(instance, ZipRequest):
        _dir = settings.ZIPS_DIR
    else:
        _dir = ""
    filename = path.join(_dir, instance.filename.name)
    if path.exists(filename) and path.isfile(filename):
        remove(filename)


class GrabberLogAdmin(admin.ModelAdmin):
    list_display = ("site", "created_at", "download_url")
    list_filter = ("site", ("created_at", DateRangeFilter))

    def get_readonly_fields(self, request, obj=None):
        if obj is not None:
            return ("filename", "created_at", "site")
        else:
            return ("created_at", "site")

    def download_url(self, obj):
        if len(obj.filename.name):
            return format_html(
                '<a href="%s">%s</a>' % (path.join(settings.STATIC_URL,
                                                   settings.GRABS_SUBDIR,
                                                   obj.filename.name),
                                         "View"))

    def get_fields(self, request, obj=None):
        if obj is not None:
            return ("created_at", "site", "created_at")
        else:
            return ("filename", "site")

    def has_add_permission(self, request):
        return False


class ZipRequestAdmin(admin.ModelAdmin):
    list_display = ("archive_request_name", "download_url", "request_status")
    list_filter = ("sites",
                   "status",
                   ("starts_from", DateRangeFilter),
                   ("ends_from", DateRangeFilter),
                   )

    def get_readonly_fields(self, request, obj=None):
        if obj is not None:
            return ("filename", "status", "starts_from", "ends_from", "sites", "delete_sources")
        else:
            return ("filename", "status")

    def get_fields(self, request, obj=None):
        if obj is not None:
            return ("status", "starts_from", "ends_from", "sites", "delete_sources")
        else:
            return ("starts_from", "ends_from", "sites", "delete_sources")

    def archive_request_name(self, obj):
        sites = " ".join([p.name for p in obj.sites.all()])
        return ("%s: %s" % (obj.id, sites))[:30]

    def download_url(self, obj):
        if len(obj.filename.name):
            return format_html(
                '<a href="%s">%s</a>' % (path.join(settings.STATIC_URL,
                                                   settings.ZIPS_SUBDIR,
                                                   obj.filename.name),
                                         "Download .zip"))

    def request_status(self, obj):
        color = {ZipRequest.Statuses.NO_DATA: "blue",
                 ZipRequest.Statuses.ERROR: "red",
                 ZipRequest.Statuses.FINISHED: "green",
                 ZipRequest.Statuses.IN_PROGRESS: "yellow"}
        return format_html(
            '<font color="%s">%s</font>' %
            (color.get(obj.status, "black"),
             dict(ZipRequest.Statuses.STATUSES).get(obj.status)))


class ReportRequestAdmin(admin.ModelAdmin):
    list_display = ("report_request_name", "download_url", "request_status")
    list_filter = ("sites",
                   "status",
                   ("starts_from", DateRangeFilter),
                   ("ends_from", DateRangeFilter),
                   )

    def get_readonly_fields(self, request, obj=None):
        if obj is not None:
            return ("filename", "status", "starts_from", "ends_from", "templates", "sites")
        else:
            return ("filename", "status")

    def get_fields(self, request, obj=None):
        if obj is not None:
            return ("status", "starts_from", "ends_from", "templates", "sites")
        else:
            return ("starts_from", "ends_from", "sites", "templates")

    def report_request_name(self, obj):
        sites = " ".join([p.name for p in obj.sites.all()])
        return ("%s: %s" % (obj.id, sites))[:30]

    def download_url(self, obj):
        if len(obj.filename.name):
            return format_html(
                '<a href="%s">%s</a>' % (path.join(settings.STATIC_URL,
                                                   settings.REPORTS_SUBDIR,
                                                   obj.filename.name),
                                         "Download .xlsx"))

    def request_status(self, obj):
        color = {ReportRequest.Statuses.NO_DATA: "blue",
                 ReportRequest.Statuses.ERROR: "red",
                 ReportRequest.Statuses.FINISHED: "green",
                 ReportRequest.Statuses.IN_PROGRESS: "yellow"}
        return format_html(
            '<font color="%s">%s</font>' %
            (color.get(obj.status, "black"),
             dict(ReportRequest.Statuses.STATUSES).get(obj.status)))

for sender in [GrabberLog, ZipRequest, ReportRequest]:
    pre_delete.connect(delete_file, sender=sender)

admin.site.register(GrabberLog, GrabberLogAdmin)
admin.site.register(ReportRequest, ReportRequestAdmin)
admin.site.register(ZipRequest, ZipRequestAdmin)
