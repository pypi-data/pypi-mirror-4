""" ``url`` module
"""

from wheezy.core.comp import urlunsplit


def urlparts(parts=None, scheme=None, netloc=None, path=None,
             query=None, fragment=None):
    """ Factory function for :py:class:`~wheezy.core.url.UrlParts` that
        create an instance :py:class:`~wheezy.core.url.UrlParts` with
        partial content.

        ``parts`` must be a 5-tuple:
        (scheme, netloc, path, query, fragment)

        >>> from wheezy.core.comp import urlsplit
        >>> parts = urlsplit('http://www.python.org/dev/peps/pep-3333')
        >>> urlparts(parts)
        urlparts('http', 'www.python.org', '/dev/peps/pep-3333', '', '')
        >>> urlparts(scheme='https', path='/test')
        urlparts('https', None, '/test', None, None)

        Otherwise raise assertion error

        >>> urlparts(('https', )) # doctest: +ELLIPSIS
        Traceback (most recent call last):
            ...
        AssertionError: ...
    """
    if not parts:
        parts = (scheme, netloc, path, query, fragment)
    return UrlParts(parts)


class UrlParts(tuple):
    """ Concrete class for :func:`urlparse.urlsplit` results.
    """

    def __init__(self, parts):
        assert len(parts) == 5, '`parts` must be a tupple of length 6'
        super(UrlParts, self).__init__()

    def __repr__(self):
        return 'urlparts' + super(UrlParts, self).__repr__()

    def geturl(self):
        """ Return the re-combined version of the original URL as a string.

            >>> from wheezy.core.comp import urlsplit
            >>> parts = urlsplit('http://www.python.org/dev/peps/pep-3333')
            >>> parts = urlparts(parts)
            >>> parts.geturl()
            'http://www.python.org/dev/peps/pep-3333'
        """
        return urlunsplit(self)

    def join(self, other):
        """ Joins with another ``UrlParts`` instance by taking
            none-empty values from ``other``. Returns new ``UrlParts``
            instance.

            Query and Fragment parts are taken unconditionally from ``other``.

            >>> from wheezy.core.comp import urlsplit
            >>> parts = urlsplit('http://www.python.org/dev/peps/pep-3333')
            >>> parts = urlparts(parts)
            >>> parts = parts.join(urlparts(scheme='https', path='/test'))
            >>> parts.geturl()
            'https://www.python.org/test'
        """
        parts = (
            other[0] or self[0],
            other[1] or self[1],
            other[2] or self[2],
            other[3],
            other[4])
        return UrlParts(parts)
