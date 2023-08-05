# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# temporary simple cache :(
class _AS_Cache(object):
    _cache = {}
    def add(self, host, site):
        rv = True
        t = self._cache.get(host,False)
        if t:
            return False
        self._cache[host] = site
        return True
    def remove(self,host):
        try:
            del self._cache[host]
            return True
        except KeyError:
            return False
    def get(self,host):
        return self._cache.get(host,False)
    def list(self):
        l = self._cache.keys()
        l.sort()
        return list((i,self._cache[i]) for i in l)

AScache = _AS_Cache()
