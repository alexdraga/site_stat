# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.utils.translation import ugettext_lazy as _


class Site(models.Model):

    url = models.TextField(verbose_name=_(u'Site URL'), unique=True, blank=False, null=False)

    class Meta:
        verbose_name = 'Site'
        db_table = 'site_urls'
        ordering = ('url')

    def __str__(self):
        return self.address


class Template(models.Model):

    site_id = models.ForeignKey(Site, verbose_name=_(u'Site URL'), on_delete=models.CASCADE)
    template = models.TextField(verbose_name=_(u'Template'), blank=False, null=False)

    class Meta:
        verbose_name = 'Templates'
        db_table = 'template'
        ordering = ('site_id')

    def __str__(self):
        return self.site_id


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


class FoundTemplatesLog(models.Model):
    TEMPLATE_RESULT = (
        (0, _('Not found')),
        (1, _('Found')),
        (2, _('Error requesting url')),
    )

    grab_id = models.ForeignKey(GrabberLog, verbose_name=_(u'Grabber log id'), on_delete=models.CASCADE)
    template_id = models.ForeignKey(Template, verbose_name=_(u'Template id'), on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    result = models.TextField(choices=TEMPLATE_RESULT, verbose_name=_(u'Template result'), blank=False, null=False)

    class Meta:
        verbose_name = 'Found templates result'
        db_table = 'templates_result_log'
        ordering = ('created_at')

    def __str__(self):
        return self.grab_id
