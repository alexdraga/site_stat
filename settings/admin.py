# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

from settings.models import Site, Template


class SiteAdmin(admin.ModelAdmin):
    list_display = ('name', 'url')

admin.site.register(Site, SiteAdmin)
admin.site.register(Template)
