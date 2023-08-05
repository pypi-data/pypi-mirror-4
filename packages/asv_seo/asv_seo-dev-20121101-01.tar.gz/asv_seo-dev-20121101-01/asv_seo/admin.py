# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from django.contrib.contenttypes import generic
from django.forms import TextInput, Textarea
#from django.db import models
from asv_seo.models import *

WideTextInput = 64
#---------------------------------------------------------------
#---------------------------------------------------------------
class SEOInline(generic.GenericStackedInline):
    model = SEO
    extra=1
    max_num=1
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs ={'rows': '3'})},
    }
#---------------------------------------------------------------
#---------------------------------------------------------------
class SEOInline_ru(SEOInline):
    fields=['title_ru','keywords_ru','description_ru']
#---------------------------------------------------------------
#---------------------------------------------------------------
class SEOInline_en(SEOInline):
    fields=['title_en','keywords_en','description_en']
#---------------------------------------------------------------
#---------------------------------------------------------------
class AsvSEO4articlesBase(generic.GenericStackedInline):
    model  = SEO4articles
    formfield_overrides = {
        models.TextField: {
            'widget': Textarea(attrs ={
                'class': 'w99',
                'cols':  '',
                'rows':  '3'
            })
        },
    }
    def get_formset(self, request, obj=None, **kwargs):
        if self.exclude:
            exclude = list(self.exclude)
        else:
            exclude = []
        if hasattr(self, '_x_exclude'):
            exclude.extend(list(self._x_exclude))
        self.exclude = exclude or None
        return super(AsvSEO4articlesBase,self).get_formset(request,obj,**kwargs)
#---------------------------------------------------------------
class AsvSEO4articlesInline(AsvSEO4articlesBase):
    extra  = 0
    max_num= 0
#---------------------------------------------------------------
#---------------------------------------------------------------
class AnalPermsAdmin(admin.ModelAdmin):
    pass
admin.site.register(AnalPerm, AnalPermsAdmin)
#---------------------------------------------------------------
#---------------------------------------------------------------
class WebCounterAdmin(admin.ModelAdmin):
    list_display = ('active', 'site', 'name')
    list_display_links = list_display
admin.site.register(WebCounter, WebCounterAdmin)
#---------------------------------------------------------------
#---------------------------------------------------------------
class RobotsTxtAdmin(admin.ModelAdmin):
    pass
admin.site.register(RobotsTxt, RobotsTxtAdmin)
#---------------------------------------------------------------
#---------------------------------------------------------------
