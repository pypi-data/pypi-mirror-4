urledit
=======
    >>> from urledit import Url

URL parsing and editing:

    >>> url = Url('forum/showthread.php?s=9b5d99fc6a61a17cc07326714500b3ab&p=728386#post728386')
    >>> url.scheme, url.netloc, url.path, url.qs, url.fragment
    ('', '', 'forum/showthread.php', 's=9b5d99fc6a61a17cc07326714500b3ab&p=728386', 'post728386')

    >>> url.scheme, url.netloc, url.fragment = 'http', 'host.com', ''
    >>> url.join()
    'http://host.com/forum/showthread.php?s=9b5d99fc6a61a17cc07326714500b3ab&p=728386'

Working with query string:

    >>> url.query
    {'p': '728386', 's': '9b5d99fc6a61a17cc07326714500b3ab'}

    >>> del url.query['s']
    >>> url.join()
    'http://host.com/forum/showthread.php?p=728386'

    >>> url.query['a'] = 1
    >>> url.query['b'] = ['x', 'y', 'z']
    >>> url.join()
    'http://host.com/forum/showthread.php?p=728386&a=1&b=x&b=y&b=z'

