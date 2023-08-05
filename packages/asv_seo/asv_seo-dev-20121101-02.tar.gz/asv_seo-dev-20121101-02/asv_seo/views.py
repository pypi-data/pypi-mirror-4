# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.http import HttpResponse, HttpResponseNotFound
from asv_seo.models import *
from asv_seo.utils import GetSite

def Yandex(request, K='', **kwargs):
    h1 = '<h1>Page not found</h1>'
    #site = GetSite(request)
    #if not site:
    #    return HttpResponseNotFound(h1)
    try:
        #A = AnalPerm.objects.get(active=True, site=site.id, key=K)
        A = AnalPerm.objects.get(active=True, key=K)
    except AnalPerm.DoesNotExist:
        return HttpResponseNotFound(h1)
    return HttpResponse('{0}'.format(A.key), content_type='text/plain')

def GetRobotsTxt(request, *args, **kwargs):
    h1 = '<h1>Page not found</h1>'
    site = GetSite(request)
    if not site:
        return HttpResponseNotFound(h1)
    try:
        R = RobotsTxt.objects.get(active=True, site=site.id)
    except RobotsTxt.DoesNotExist:
        return HttpResponseNotFound(h1)
    return HttpResponse('{0}'.format(R.code), content_type='text/plain')

