# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

from grabber.models import Site, GrabberLog, Templates


class GrabberLogAdmin(admin.ModelAdmin):
    list_display = ('site', 'filename', 'created_at')

    def get_readonly_fields(self, request, obj=None):
        if obj is not None:
            return ["filename", "created_at", "site"]


class SiteAdmin(admin.ModelAdmin):
    list_display = ('name', 'url')

admin.site.register(Site, SiteAdmin)
admin.site.register(GrabberLog, GrabberLogAdmin)
admin.site.register(Templates)
