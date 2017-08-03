# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

from grabber.models import Site, GrabberLog

admin.site.register(Site)
admin.site.register(GrabberLog)
