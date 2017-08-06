# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import os

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



class Template(models.Model):
    site = models.ForeignKey(Site, verbose_name=_(u'Имя сайта'))
    template = models.TextField(verbose_name=_(u'Текст шаблона'), unique=True)

    class Meta:
        verbose_name = _('Шаблон')
        verbose_name_plural = ("Шаблоны")

    def __str__(self):
        return "%s: %s" % (self.site.name, self.template[:10])


class ReportRequest(models.Model):
    class Statuses():
        IN_PROGRESS = 0
        ERROR = 1
        FINISHED = 2
        STATUSES = ((IN_PROGRESS, "Не обработан"),
                    (ERROR, "Ошибка"),
                    (FINISHED, "Выполнен"))
    starts_from = models.DateTimeField(verbose_name=_(u'С'))
    ends_from = models.DateTimeField(verbose_name=_(u'До'))
    sites = models.ManyToManyField(Site, verbose_name=_(u'Для сайтов'))
    templates = models.ManyToManyField(Template, verbose_name=_(u'Шаблоны'))
    status = models.IntegerField(verbose_name=_(u'Статус'),
                                 default=Statuses.IN_PROGRESS,
                                 choices=Statuses.STATUSES)
    filename = models.FileField(verbose_name=_(u'Файл'), )


class ZipRequest(models.Model):
    class Statuses():
        IN_PROGRESS = 0
        ERROR = 1
        FINISHED = 2
        STATUSES = ((IN_PROGRESS, "Не обработан"),
                    (ERROR, "Ошибка"),
                    (FINISHED, "Выполнен"))
    starts_from = models.DateTimeField(verbose_name=_(u'С'))
    ends_from = models.DateTimeField(verbose_name=_(u'До'))
    sites = models.ManyToManyField(Site, verbose_name=_(u'Для сайтов'))
    status = models.IntegerField(verbose_name=_(u'Статус'),
                                 default=Statuses.IN_PROGRESS,
                                 choices=Statuses.STATUSES)
    filename = models.FileField(verbose_name=_(u'Файл'), null=True)
