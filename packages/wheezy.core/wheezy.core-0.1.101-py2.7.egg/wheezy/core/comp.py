
""" ``comp`` module.
"""

import sys


PY_MAJOR = sys.version_info[0]
PY_MINOR = sys.version_info[1]
PY2 = PY_MAJOR == 2
PY3 = PY_MAJOR >= 3


if PY3:  # pragma: nocover
    from queue import Queue
    xrange = range
    str_type = str

    def ntob(n, encoding):
        """ Converts native string to bytes
        """
        return n.encode(encoding)

    def bton(b, encoding):
        """ Converts bytes to native string
        """
        return b.decode(encoding)

    u = lambda s: s

else:  # pragma: nocover
    from Queue import Queue  # noqa
    xrange = xrange
    str_type = unicode

    def ntob(n, encoding):  # noqa
        """ Converts native string to bytes
        """
        return n

    def bton(b, encoding):  # noqa
        """ Converts bytes to native string
        """
        return b

    u = lambda s: unicode(s, "unicode_escape")


if PY2 and PY_MINOR == 4:  # pragma: nocover
    __import__ = __import__
else:  # pragma: nocover
    # perform absolute import
    __saved_import__ = __import__
    __import__ = lambda n, g=None, l=None, f=None: \
        __saved_import__(n, g, l, f, 0)


try:  # pragma: nocover
    #from collections import defaultdict
    defaultdict = __import__(
        'collections', None, None, ['defaultdict']).defaultdict
except AttributeError:  # pragma: nocover

    class defaultdict(dict):

        def __init__(self, default_factory=None, *args, **kwargs):
            if default_factory and not hasattr(default_factory, '__call__'):
                raise TypeError('first argument must be callable')
            super(defaultdict, self).__init__(*args, **kwargs)
            self.default_factory = default_factory

        def __getitem__(self, key):
            try:
                return dict.__getitem__(self, key)
            except KeyError:
                return self.__missing__(key)

        def __missing__(self, key):
            if self.default_factory is None:
                raise KeyError(key)
            self[key] = value = self.default_factory()
            return value

        def __reduce__(self):
            if self.default_factory is None:
                args = tuple()
            else:
                args = self.default_factory,
            return type(self), args, None, None, self.items()

        def __repr__(self):
            return 'defaultdict(%s, %s)' % (self.default_factory,
                                            dict.__repr__(self))

try:  # pragma: nocover
    from email.utils import parsedate
except ImportError:  # pragma: nocover
    import time
    parsedate = lambda s: time.strptime(s, "%a, %d %b %Y %H:%M:%S GMT")  # noqa

if PY3:  # pragma: nocover
    from urllib.parse import urlsplit
    from urllib.parse import urlunsplit
else:  # pragma: nocover
    from urlparse import urlsplit  # noqa
    from urlparse import urlunsplit  # noqa

if PY3:  # pragma: nocover
    ref_gettext = lambda t: t.gettext
else:  # pragma: nocover
    ref_gettext = lambda t: t.ugettext  # noqa

if PY3 or PY2 and PY_MINOR >= 6:  # pragma: nocover
    m = __import__('json', None, None, ['JSONEncoder', 'dumps', 'loads'])
    SimpleJSONEncoder = m.JSONEncoder
    json_dumps = m.dumps
    json_loads = m.loads
    del m
else:  # pragma: nocover
    try:
        from simplejson import JSONEncoder as SimpleJSONEncoder
        from simplejson import dumps
        from simplejson import loads as json_loads  # noqa

        def json_dumps(obj, **kw):  # noqa
            return dumps(obj, use_decimal=False, **kw)
    except ImportError:
        SimpleJSONEncoder = object  # noqa

        def json_dumps(obj, **kw):  # noqa
            raise NotImplementedError('JSON encoder is required.')

        def json_loads(s, **kw):  # noqa
            raise NotImplementedError('JSON decoder is required.')
