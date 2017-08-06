# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os

from django.contrib import admin
from django.db.models.signals import pre_delete
from django.dispatch.dispatcher import receiver

from reports.models import GrabberLog, ReportRequest, ZipRequest


class GrabberLogAdmin(admin.ModelAdmin):
    list_display = ('site', 'filename', 'created_at')

    def get_readonly_fields(self, request, obj=None):
        if obj is not None:
            return ["filename", "created_at", "site"]
        else:
            return ["created_at", "site"]

    @receiver(pre_delete, sender=GrabberLog)
    def grabberlog_delete(sender, instance, **kwargs):
        if os.path.exists(instance.filename.name):
            os.remove(instance.filename.name)


class ZipRequestAdmin(admin.ModelAdmin):
    list_display = ('archive_request_name', 'filename', 'status')

    def get_readonly_fields(self, request, obj=None):
        if obj is not None:
            return ["filename", "status", "starts_from", "ends_from", "sites"]
        else:
            return ["filename", "status"]

    def archive_request_name(self, obj):
        sites = " ".join([p.name for p in obj.sites.all()])
        return "%s: %s" % (sites, obj.id)

    @receiver(pre_delete, sender=ZipRequest)
    def grabberlog_delete(sender, instance, **kwargs):
        if os.path.exists(instance.filename.name):
            os.remove(instance.filename.name)


class ReportRequestAdmin(admin.ModelAdmin):
    list_display = ('report_request_name','filename', 'status')

    def get_readonly_fields(self, request, obj=None):
        if obj is not None:
            return ["filename", "status", "starts_from", "ends_from", "templates", "sites"]
        else:
            return ["filename", "status"]

    def report_request_name(self, obj):
        sites = " ".join([p.name for p in obj.sites.all()])
        return "%s: %s" % (sites, obj.id)

    @receiver(pre_delete, sender=ReportRequest)
    def grabberlog_delete(sender, instance, **kwargs):
        if os.path.exists(instance.filename.name):
            os.remove(instance.filename.name)

admin.site.register(GrabberLog, GrabberLogAdmin)
admin.site.register(ReportRequest, ReportRequestAdmin)
admin.site.register(ZipRequest, ZipRequestAdmin)
