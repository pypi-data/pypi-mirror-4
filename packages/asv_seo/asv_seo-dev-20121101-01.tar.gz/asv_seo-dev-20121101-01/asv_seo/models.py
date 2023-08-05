# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.db import models
from django.db.models.signals import *
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site
from django.core.exceptions import *

#from mptt.models import MPTTModel
#import re

#---------------------------------------------------------------
#---------------------------------------------------------------
class SEO(models.Model):
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object=generic.GenericForeignKey('content_type','object_id')
    #
    title_en   =models.CharField(blank=True, max_length=128, help_text='заголовок английской страницы')
    title_ru   =models.CharField(blank=True, max_length=128, help_text='заголовок русской страницы')
    keywords_en=models.TextField(blank=True, help_text='введите английские ключевые слова для страницы через запятую.')
    keywords_ru=models.TextField(blank=True, help_text='введите русские ключевые слова для страницы через запятую.')
    description_en=models.TextField(blank=True, help_text='опишите в 2-3 фразы о чем эта страница на английском языке')
    description_ru=models.TextField(blank=True, help_text='опишите в 2-3 фразы о чем эта страница на русском языке')
    de     = models.DateTimeField(auto_now_add=True)
    lm     = models.DateTimeField(auto_now=True)
    #----------
    def __unicode__(self):
        rv = self.title_ru if self.title_ru else self.title_en
        return rv
    class Meta:
        ordering = ('content_type', 'de')
        #unique_together = ('tree_id','level','slug')
        verbose_name='SEO'
        verbose_name_plural='SEO'
#---------------------------------------------------------------
#---------------------------------------------------------------
class SEO4articles(models.Model):
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object=generic.GenericForeignKey('content_type','object_id')
    #
    lang       =models.CharField(max_length=2, default='ru', verbose_name='язык', blank=True, editable=False)
    title      =models.CharField(blank=True, max_length=128)
    keywords   =models.TextField(blank=True, help_text='введите через запятую ключевые слова для страницы.')
    description=models.TextField(blank=True, help_text='опишите в 2-3 фразы о чем эта страница')
    de     = models.DateTimeField(auto_now_add=True)
    lm     = models.DateTimeField(auto_now=True)
    #----------
    def get_document(self):
        return self.content_object
    def __unicode__(self):
        rv = '[{0}] {1}'.format(self.lang, self.title)
        return rv
    def delete(self, **kwargs):
        try:
            # update Djapian's index, if it is!
            self.__class__.indexer.delete(self)
        except Exception as e:
            if settings.DEBUG:
                print('asv_seo__SEO4articles[{0}].delete::{1}'.format(self.id,e))
        super(SEO4articles, self).delete(**kwargs)
    def save(self, **kwargs):
        super(SEO4articles, self).save(**kwargs)
        try:
            # update Djapian's index, if it is!
            self.__class__.indexer.update()
        except Exception as e:
            if settings.DEBUG:
                print('asv_seo__SEO4articles[{0}].save::{1}'.format(self.id,e))
    #
    class Meta:
        ordering = ('content_type', 'de')
        #unique_together = ('tree_id','level','slug')
        verbose_name='SEO'
        verbose_name_plural='SEO'
#---------------------------------------------------------------
#---------------------------------------------------------------
class AnalPerm(models.Model):
    _analsystem_choices = (
        ('YANDEX',   'Yandex'),
        ('GOOGLE', 'Google'),
        )
    active=models.BooleanField(default=True)
    system=models.SlugField(max_length=32, choices=_analsystem_choices, verbose_name='в системе')
    key   =models.SlugField(max_length=512, unique=True, db_index=True)
    name  =models.CharField(max_length=512, blank=True)
    de    = models.DateTimeField(auto_now_add=True)
    lm    = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        a = self.name or self.key
        return '{0}: {1}'.format(self.system, a)

    def save(self, **kwargs):
        if self.key.startswith('yandex_') or self.key.endswith('.txt'):
            q1=self.key.find('_')
            q1 = q1 if q1 >0 else 0
            q2=self.key.find('.')
            q2 = q2 if q2 >0 else 0

            if q1 and q2:
                self.key = self.key[q1+1:q2]
            elif q1:
                self.key = self.key[q1+1:]
            elif q2:
                self.key = self.key[:q2]
        super(AnalPerm, self).save(**kwargs)

    class Meta:
        ordering = ('system', 'name', 'de')
        verbose_name='авторизация в системе аналитики'
        verbose_name_plural='авторизации в системе аналитики'
#---------------------------------------------------------------
#---------------------------------------------------------------
class WebCounter(models.Model):
    active= models.BooleanField(default=True)
    site  = models.ForeignKey(Site)
    name  = models.CharField(max_length=128, blank=True)
    code  = models.TextField(help_text='Введите код счетчика.')
    de    = models.DateTimeField(auto_now_add=True)
    lm    = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        a = self.name or 'Unnamed counter: {0}'.format(de)
        return a

    #def save(self, **kwargs):
    #    super(WebCounter, self).save(**kwargs)

    class Meta:
        ordering = ('site', 'lm')
        verbose_name='код счетчика'
        verbose_name_plural='коды счетчиков'
#---------------------------------------------------------------
#---------------------------------------------------------------
class RobotsTxt(models.Model):
    active= models.BooleanField(default=True)
    site  = models.ForeignKey(Site)
    code  = models.TextField(help_text='тело файла robots.txt')
    de    = models.DateTimeField(auto_now_add=True)
    lm    = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return 'robots.txt for site {0}'.format(self.site)

    #def save(self, **kwargs):
    #    super(WebCounter, self).save(**kwargs)

    class Meta:
        ordering = ('site', 'lm')
        verbose_name='файл robots.txt'
        verbose_name_plural='файлы robots.txt'
#---------------------------------------------------------------
#---------------------------------------------------------------
