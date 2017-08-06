# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.db import models
from django.utils.translation import ugettext_lazy as _


class Site(models.Model):
    name = models.CharField(max_length=200, verbose_name=_(u'Name'), unique=True)
    url = models.URLField(verbose_name=_(u'URL'), unique=True)

    class Meta:
        verbose_name = _('Site')
        verbose_name_plural = ("Sites")

    def __str__(self):
        return self.name


class Template(models.Model):
    site = models.ForeignKey(Site, verbose_name=_(u'Sitename'))
    template = models.TextField(verbose_name=_(u'Template text'), unique=True)

    class Meta:
        verbose_name = _('Template')
        verbose_name_plural = ("Templates")

    def __str__(self):
        return "%s: %s" % (self.site.name, self.template[:10])
