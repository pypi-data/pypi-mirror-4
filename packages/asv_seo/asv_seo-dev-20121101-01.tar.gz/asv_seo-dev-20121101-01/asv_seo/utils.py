# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib.sites.models import Site
from django.dispatch import receiver
from asv_seo.models import *
from asv_seo.cache import AScache

def GetSite(request):
    h = request.get_host()
    a = h.find(':')
    if a >0:
        h = h[:a]
    ss = AScache.get(h)
    if ss:
        return ss
    try:
        ss = Site.objects.get(domain=h)
        AScache.add(h,ss)
        return ss
    except MultipleObjectsReturned:
        ss = Site.objects.filter(domain=h).order_by('pk')[0]
        AScache.add(h,ss)
        return ss
    except ObjectDoesNotExist:
        pass
    sites = []
    ss = Site.objects.all().order_by('pk')
    for i in ss:
        if i.domain[0] == '.' and (h.endswith(i.domain) or '.{0}'.format(h) == i.domain):
            sites.append(i)
    y = len(sites)
    k = None
    if y < 1:
        pass
    elif y == 1:
        k = sites[0]
        AScache.add(h,k)
    else:
        y = 0
        for i in sites:
            t = len(i.domain)
            if  t > y:
                k = i
                y = t
        AScache.add(h,k)
    return k

def remove_recs_from_cache(sender, **kwargs):
    sss = kwargs.get('instance')
    if sss:
        try:
            ss = sender.objects.get(pk=sss.pk)
            for a in AScache.list():
                if a[1]==ss:
                    AScache.remove(a[0])
        except sender.DoesNotExist:
            pass
            #

@receiver(pre_save, sender=Site)
def modify_site_rec(sender, **kwargs):
    remove_recs_from_cache(sender, **kwargs)

@receiver(pre_delete, sender=Site)
def remove_site_rec(sender, **kwargs):
    remove_recs_from_cache(sender, **kwargs)
