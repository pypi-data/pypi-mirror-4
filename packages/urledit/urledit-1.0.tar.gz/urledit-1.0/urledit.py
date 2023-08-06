'''
urledit
======
URL parsing and editing in the object or functional style.

    >>> from urledit import urledit
    >>> url = 'forum/showthread.php?s=9b5d99fc6a61a17cc07326714500b3ab&p=728386#post728386'

Functional style
----------------
    >>> urledit(url)(scheme='http')(netloc='host.com')(fragment=''
    ... ).param(s=None).param(a=1).param(b=['x', 'y', 'z']).join()
    'http://host.com/forum/showthread.php?p=728386&a=1&b=x&b=y&b=z'

or

    >>> urledit(url, scheme='http', netloc='host.com', fragment=''
    ... ).param(s=None, a=1, b=['x', 'y', 'z']).join()
    'http://host.com/forum/showthread.php?p=728386&a=1&b=x&b=y&b=z'

Object style
------------
    >>> u = urledit(url)
    >>> u.scheme, u.netloc, u.path, u.qs, u.fragment
    ('', '', 'forum/showthread.php', 's=9b5d99fc6a61a17cc07326714500b3ab&p=728386', 'post728386')

    >>> u.scheme, u.netloc, u.fragment = 'http', 'host.com', ''
    >>> u.join()
    'http://host.com/forum/showthread.php?s=9b5d99fc6a61a17cc07326714500b3ab&p=728386'

Working with query string:

    >>> u.query
    {'p': '728386', 's': '9b5d99fc6a61a17cc07326714500b3ab'}

    >>> del u.query['s']
    >>> u.join()
    'http://host.com/forum/showthread.php?p=728386'

    >>> u.query['a'] = 1
    >>> u.query['b'] = ['x', 'y', 'z']
    >>> u.join()
    'http://host.com/forum/showthread.php?p=728386&a=1&b=x&b=y&b=z'
'''
import urllib
import urlparse

__version__ = '1.0'


class urledit(object):
    ALLOWED_FRAGMENTS = ('scheme', 'netloc', 'path', 'fragment')

    def __init__(self, url, **kwargs):
        parts = list(urlparse.urlsplit(url))
        self.scheme, self.netloc, self.path, self._qs, self.fragment = parts
        self._query = None
        self._qs_changed = False
        if kwargs:
            self(**kwargs)

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

    def __call__(self, **kwargs):
        for k, v in kwargs.items():
            assert k in self.ALLOWED_FRAGMENTS, 'Wrong fragment: %s' % k
            setattr(self, k, v)
        return self

    def param(self, *args, **kwargs):
        for k, v in args:
            self._set_param(k, v)
        for k, v in kwargs.items():
            self._set_param(k, v)
        return self

    def _set_param(self, k, v):
        if v is None:
            self.query.pop(k, None)
        else:
            self.query[k] = v

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
