# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.db import models
from django.utils.translation import ugettext_lazy as _


class Site(models.Model):
    url = models.TextField(verbose_name=_(u'Адрес сайта'), unique=True)
    name = models.TextField(verbose_name=_(u'Имя сайта'), unique=True)

    class Meta:
        verbose_name = _('Сайт')
        verbose_name_plural = ("Сайты")

    def __str__(self):
        return self.name


class GrabberLog(models.Model):
    site = models.ForeignKey(Site, verbose_name=_(u'Имя сайта'), on_delete=models.CASCADE)
    created_at = models.DateTimeField(verbose_name=_(u'Создан'), auto_now_add=True)
    filename = models.FileField(verbose_name=_(u'Файл'),)

    class Meta:
        verbose_name = _('Сохранённая страница')
        verbose_name_plural = ("Архив")

    def __str__(self):
        return "%s: %s" % (self.site, self.created_at)


class Templates(models.Model):
    site = models.ForeignKey(Site, verbose_name=_(u'Имя сайта'), on_delete=models.CASCADE)
    template = models.TextField(verbose_name=_(u'Текст шаблона'), unique=True)

    class Meta:
        verbose_name = _('Шаблон')
        verbose_name_plural = ("Шаблоны")

    def __str__(self):
        return "%s: %s" % (self.site, self.template[:10])
