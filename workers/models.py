# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.utils.translation import ugettext_lazy as _


class Worker(models.Model):

    class WorkerNames():
        GRAB = "grab"
        ZIP = "zip"
        REPORT = "report"
        STATUSES = ((GRAB, "Grab worker"),
                    (ZIP, 'Zip worker'),
                    (REPORT, "Report worker"))
    worker_name = models.CharField(verbose_name=_(u'Worker name'),
                                   max_length=20,
                                   choices=WorkerNames.STATUSES,
                                   unique=True)
    timeout = models.IntegerField(verbose_name=_(u'Worker timeout, s'), default=5)
    next_run = models.DateTimeField(verbose_name=_(u'Next run'))
    heartbeat = models.DateTimeField(verbose_name=_(u'Heartbeat'))

    class Meta:
        verbose_name = _('Worker')
        verbose_name_plural = _("Workers")

    def __str__(self):
        return self.worker_name
