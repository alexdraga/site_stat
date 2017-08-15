# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.db import models
from django.utils.translation import ugettext_lazy as _

from input_data.models import Site, Template


class GrabberLog(models.Model):
    site = models.ForeignKey(Site, verbose_name=_(u'Sitename'), on_delete=models.CASCADE)
    created_at = models.DateTimeField(verbose_name=_(u'Created at'))
    filename = models.FileField(verbose_name=_(u'File'), )

    class Meta:
        verbose_name = _('Snapshot')
        verbose_name_plural = _("Snapshots")
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

    class Detalisation():
        DAY = 0
        HOUR = 1
        FULL = 2
        DETALISATIONS = ((DAY, "By day"),
                         (HOUR, 'By hour'),
                         (FULL, "Full"))

    starts_from = models.DateTimeField(verbose_name=_(u'Start date'))
    ends_from = models.DateTimeField(verbose_name=_(u'End date'))
    created_at = models.DateTimeField(verbose_name=_(u'Created at'), auto_now_add=True)
    sites = models.ManyToManyField(Site, verbose_name=_(u'Site list'))
    templates = models.ManyToManyField(Template, verbose_name=_(u'Templates'))
    status = models.IntegerField(verbose_name=_(u'Status'),
                                 default=Statuses.IN_PROGRESS,
                                 choices=Statuses.STATUSES)
    filename = models.FileField(verbose_name=_(u'File'), )
    detalisation = models.IntegerField(verbose_name=_(u'Detalisation'),
                                       default=Detalisation.DAY,
                                       choices=Detalisation.DETALISATIONS)

    class Meta:
        verbose_name = _('Report')
        verbose_name_plural = _("Reports")
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

    starts_from = models.DateTimeField(verbose_name=_(u'Start date'))
    ends_from = models.DateTimeField(verbose_name=_(u'End date'))
    created_at = models.DateTimeField(verbose_name=_(u'Created at'), auto_now_add=True)
    sites = models.ManyToManyField(Site, verbose_name=_(u'Sites'))
    status = models.IntegerField(verbose_name=_(u'Status'),
                                 default=Statuses.IN_PROGRESS,
                                 choices=Statuses.STATUSES)
    filename = models.FileField(verbose_name=_(u'File'), null=True)
    delete_sources = models.BooleanField(
        verbose_name=_(u'Delete original files from host'), default=False)

    class Meta:
        verbose_name = _('ZIP')
        verbose_name_plural = _("ZIPs")
        ordering = ['-id']
