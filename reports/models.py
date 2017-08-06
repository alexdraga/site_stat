# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.db import models
from django.utils.translation import ugettext_lazy as _

from settings.models import Site, Template


class GrabberLog(models.Model):
    site = models.ForeignKey(Site, verbose_name=_(u'Sitename'), on_delete=models.CASCADE)
    created_at = models.DateTimeField(verbose_name=_(u'Created at'), auto_now_add=True)
    filename = models.FileField(verbose_name=_(u'File'),)

    class Meta:
        verbose_name = _('Saved page')
        verbose_name_plural = ("Saved pages")
        ordering = ['-id']

    def __str__(self):
        return "%s: %s" % (self.site, self.created_at)


class ReportRequest(models.Model):
    class Statuses():
        IN_PROGRESS = 0
        ERROR = 1
        NO_DATA = 2
        FINISHED = 3
        STATUSES = ((IN_PROGRESS, "In progress"),
                    (NO_DATA, 'No data'),
                    (ERROR, "Error"),
                    (FINISHED, "Finished"))
    starts_from = models.DateTimeField(verbose_name=_(u'From'))
    ends_from = models.DateTimeField(verbose_name=_(u'Till'))
    sites = models.ManyToManyField(Site, verbose_name=_(u'Site list'))
    templates = models.ManyToManyField(Template, verbose_name=_(u'Templates'))
    status = models.IntegerField(verbose_name=_(u'Status'),
                                 default=Statuses.IN_PROGRESS,
                                 choices=Statuses.STATUSES)
    filename = models.FileField(verbose_name=_(u'File'), )

    class Meta:
        verbose_name = _('Report')
        verbose_name_plural = ("Reports")
        ordering = ['-id']


class ZipRequest(models.Model):
    class Statuses():
        IN_PROGRESS = 0
        ERROR = 1
        NO_DATA = 2
        FINISHED = 3
        STATUSES = ((IN_PROGRESS, "In progress"),
                    (NO_DATA, 'No data'),
                    (ERROR, "Error"),
                    (FINISHED, "Finished"))
    starts_from = models.DateTimeField(verbose_name=_(u'From'))
    ends_from = models.DateTimeField(verbose_name=_(u'Till'))
    sites = models.ManyToManyField(Site, verbose_name=_(u'Site list'))
    status = models.IntegerField(verbose_name=_(u'Status'),
                                 default=Statuses.IN_PROGRESS,
                                 choices=Statuses.STATUSES)
    filename = models.FileField(verbose_name=_(u'File'), null=True)

    class Meta:
        verbose_name = _('ZIP')
        verbose_name_plural = ("ZIPs")
        ordering = ['-id']