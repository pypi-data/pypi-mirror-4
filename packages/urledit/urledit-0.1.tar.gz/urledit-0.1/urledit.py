#!/usr/bin/env python
# -*- coding: utf-8 -*-
import urllib
import urlparse

__version__ = '0.1'


class Url(object):
    def __init__(self, url):
        parts = list(urlparse.urlsplit(url))
        self.scheme, self.netloc, self.path, self._qs, self.fragment = parts
        self._query = None
        self._qs_changed = False

    @property
    def query(self):
        self._qs_changed = True
        if not self._query:
            self._query = QS(self._qs)
        return self._query

    @property
    def qs(self):
        if self._qs_changed:
            return self.query.join()
        return self._qs

    def join(self):
        parts = [self.scheme, self.netloc, self.path, self.qs, self.fragment]
        return urlparse.urlunsplit(parts)

    __unicode__ = lambda(self): self.join()
    __str__ = lambda(self): str(self.__unicode__())


class QS(dict):
    def __init__(self, qs):
        super(QS, self).__init__()
        pairs = urlparse.parse_qsl(qs)
        self.order = []
        for k, v in pairs:
            if k not in self.order:
                self.order.append(k)
            if k in self:
                if not isinstance(self[k], list):
                    self[k] = [self[k]]
                self[k].append(v)
            else:
                self[k] = v

    def join(self):
        pairs = []
        for k, vs in self.iteritems():
            if not isinstance(vs, list):
                vs = [vs]
            for v in vs:
                pairs.append((k, v))
        pairs.sort(key=lambda x: self.order.index(x[0])
                if x[0] in self.order else len(self.order))
        return urllib.urlencode(pairs)


if __name__ == '__main__':
    import doctest
    doctest.testmod(verbose=True)
