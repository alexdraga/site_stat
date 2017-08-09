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
    if path.exists(filename):
        remove(filename)


class GrabberLogAdmin(admin.ModelAdmin):
    list_display = ("site", "created_at", "show_firm_url")
    list_filter = (("created_at", DateRangeFilter),)

    def get_readonly_fields(self, request, obj=None):
        if obj is not None:
            return ("filename", "created_at", "site")
        else:
            return ("created_at", "site")

    def show_firm_url(self, obj):
        if obj.filename is not None:
            return format_html(
                '<a href="%s">%s</a>' % (path.join(settings.STATIC_URL,
                                                   settings.GRABS_SUBDIR,
                                                   obj.filename.name),
                                         "View"))


class ZipRequestAdmin(admin.ModelAdmin):
    list_display = ("archive_request_name", "show_firm_url", "status")
    list_filter = ("sites",
                   "status",
                   ("starts_from", DateRangeFilter),
                   ("ends_from", DateRangeFilter),
                   )

    def get_readonly_fields(self, request, obj=None):
        if obj is not None:
            return ("filename", "status", "starts_from", "ends_from", "sites")
        else:
            return ("filename", "status")

    def archive_request_name(self, obj):
        sites = " ".join([p.name for p in obj.sites.all()])
        return "%s: %s" % (obj.id, sites)

    def show_firm_url(self, obj):
        if obj.filename is not None:
            return format_html(
                '<a href="%s">%s</a>' % (path.join(settings.STATIC_URL,
                                                   settings.ZIPS_SUBDIR,
                                                   obj.filename.name),
                                         "Download .zip"))


class ReportRequestAdmin(admin.ModelAdmin):
    list_display = ("report_request_name", "show_firm_url", "status")
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

    def report_request_name(self, obj):
        sites = " ".join([p.name for p in obj.sites.all()])
        return "%s: %s" % (obj.id, sites)

    def show_firm_url(self, obj):
        if obj.filename is not None:
            return format_html(
                '<a href="%s">%s</a>' % (path.join(settings.STATIC_URL,
                                                   settings.REPORTS_SUBDIR,
                                                   obj.filename.name),
                                         "Download .xlsx"))


for sender in [GrabberLog, ZipRequest, ReportRequest]:
    pre_delete.connect(delete_file, sender=sender)

admin.site.register(GrabberLog, GrabberLogAdmin)
admin.site.register(ReportRequest, ReportRequestAdmin)
admin.site.register(ZipRequest, ZipRequestAdmin)
