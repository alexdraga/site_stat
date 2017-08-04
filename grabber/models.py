# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.db import models
from django.utils.translation import ugettext_lazy as _


class Site(models.Model):
    url = models.TextField(verbose_name=_(u'Site URL'), unique=True)
    name = models.TextField(verbose_name=_(u'Site name'), unique=True)

    class Meta:
        verbose_name = _('Site')

    def __str__(self):
        return self.name


class GrabberLog(models.Model):
    site = models.ForeignKey(Site, verbose_name=_(u'Site URL'), on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    filename = models.FileField(verbose_name=_(u'Filename'))

    class Meta:
        verbose_name = _('Grabber Log')

    def __str__(self):
        return "%s: %s" % (self.site, self.created_at)
