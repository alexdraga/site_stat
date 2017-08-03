# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.utils.translation import ugettext_lazy as _


class Site(models.Model):

    url = models.TextField(verbose_name=_(u'Site URL'), unique=True, blank=False, null=False)
    name = models.TextField(verbose_name=_(u'Site name'), unique=True, blank=False, null=False)

    class Meta:
        verbose_name = 'Site'
        db_table = 'site_urls'
        ordering = ('url')

    def __str__(self):
        return self.name


class GrabberLog(models.Model):

    site_id = models.ForeignKey(Site, verbose_name=_(u'Site URL'), on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    filename = models.TextField(verbose_name=_(u'Filename'), blank=False, null=False)

    class Meta:
        verbose_name = 'Grabber Log'
        db_table = 'grabber_log'
        ordering = ('created_at')

    def __str__(self):
        return self.filename
