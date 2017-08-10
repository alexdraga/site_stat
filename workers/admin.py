# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from django.utils import timezone
from django.utils.html import format_html

from workers.models import Worker


class WorkerAdmin(admin.ModelAdmin):
    list_display = ("worker_name", "timeout", "next_run", "worker_status")

    def get_readonly_fields(self, request, obj=None):
        if obj is not None:
            return ("worker_name", "heartbeat")
        else:
            return tuple()

    def worker_status(self, obj):
        if timezone.now() > obj.heartbeat:
            return format_html('<font color="red"><b>STOPPED</b></font>')
        else:
            return format_html('<font color="green">ACTIVE</font>')

    def has_add_permission(self, request):
        return False


admin.site.register(Worker, WorkerAdmin)
