
""" ``datetime`` module.
"""

from time import localtime
from time import mktime

from wheezy.core.comp import parsedate
from wheezy.core.introspection import import_name

# The lines below are equivalent to:
# from datetime import timedelta
# However it is not used due module name confict
# since the use of relative imports by default.
# absolute imports are available since python 2.5,
# however we want keep compatibility with python 2.4
datetime = import_name('datetime.datetime')
time = import_name('datetime.time')
timedelta = import_name('datetime.timedelta')
tzinfo = import_name('datetime.tzinfo')


ZERO = timedelta(0)
WEEKDAYS = ("Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun")
MONTHS = (
    None, "Jan", "Feb", "Mar", "Apr", "May", "Jun",
    "Jul", "Aug", "Sep", "Oct", "Nov", "Dec")


def format_http_datetime(stamp):
    """ Formats datetime to a string following rfc1123 pattern.

        >>> now = datetime(2011, 9, 19, 10, 45, 30, 0, UTC)
        >>> format_http_datetime(now)
        'Mon, 19 Sep 2011 10:45:30 GMT'

        if timezone is not set in datetime instance the ``stamp``
        is assumed to be in UTC (``datetime.utcnow``).

        >>> now = datetime(2011, 9, 19, 10, 45, 30, 0)
        >>> format_http_datetime(now)
        'Mon, 19 Sep 2011 10:45:30 GMT'

        >>> now = datetime.utcnow()
        >>> assert format_http_datetime(now)

        if ``stamp`` is a string just return it

        >>> format_http_datetime('x')
        'x'

        >>> format_http_datetime(100) # doctest: +ELLIPSIS
        Traceback (most recent call last):
            ...
        TypeError: ...
    """
    if isinstance(stamp, datetime):
        if stamp.tzinfo:
            stamp = stamp.astimezone(UTC).timetuple()
        else:
            stamp = localtime(mktime(stamp.timetuple()))
    elif isinstance(stamp, str):
        return stamp
    else:
        raise TypeError('Expecting type ``datetime.datetime``.')

    year, month, day, hh, mm, ss, wd, y, z = stamp
    return "%s, %02d %3s %4d %02d:%02d:%02d GMT" % (
        WEEKDAYS[wd], day, MONTHS[month], year, hh, mm, ss
    )


def format_iso_datetime(stamp):
    """ Return a string representing the date and time in ISO 8601 format.
        If the time is in UTC, adds a 'Z' directly after the time without
        a space.

        see http://en.wikipedia.org/wiki/ISO_8601.

        >>> class EET(tzinfo):
        ...     def utcoffset(self, dt):
        ...         return timedelta(minutes=120)
        ...     def dst(self, dt):
        ...         return timedelta()
        >>> format_iso_datetime(datetime(2012, 2, 22, 12, 52, 29, 300))
        '2012-02-22T12:52:29'
        >>> format_iso_datetime(datetime(2012, 2, 22, 12, 52, 29, 300,
        ...     tzinfo=UTC))
        '2012-02-22T12:52:29Z'
        >>> format_iso_datetime(datetime(2012, 2, 22, 12, 52, 29, 300,
        ...     tzinfo=EET()))
        '2012-02-22T12:52:29+02:00'
    """
    if stamp.tzinfo:
        if stamp.utcoffset() == ZERO:
            return datetime(*stamp.timetuple()[:6]).isoformat() + 'Z'
    if stamp.microsecond:
        stamp = stamp.replace(microsecond=0)
    return stamp.isoformat()


def format_iso_time(stamp):
    """ Return a string representing the time in ISO 8601 format.
        If the time is in UTC, adds a 'Z' directly after the time without
        a space.

        see http://en.wikipedia.org/wiki/ISO_8601.

        >>> class EET(tzinfo):
        ...     def utcoffset(self, dt):
        ...         return timedelta(minutes=120)
        ...     def dst(self, dt):
        ...         return timedelta()
        >>> format_iso_time(time(12, 52, 29, 300))
        '12:52:29'
        >>> format_iso_time(time(12, 52, 29, 300,
        ...     tzinfo=UTC))
        '12:52:29Z'
        >>> format_iso_time(time(12, 52, 29, 300,
        ...     tzinfo=EET()))
        '12:52:29+02:00'
    """
    if stamp.microsecond:
        stamp = stamp.replace(microsecond=0)
    if stamp.tzinfo:
        if stamp.utcoffset() == ZERO:
            return stamp.replace(tzinfo=None).isoformat() + 'Z'
        else:
            return stamp.isoformat()
    else:
        return stamp.isoformat()


def parse_http_datetime(stamp):
    """ Parses a string in rfc1123 format to ``datetime``.

        >>> parse_http_datetime('Mon, 19 Sep 2011 10:45:30 GMT')
        datetime.datetime(2011, 9, 19, 10, 45, 30)
    """
    return datetime.fromtimestamp(mktime(parsedate(stamp)))


def total_seconds(delta):
    """ Returns a total number of seconds for the given delta.

        ``delta`` can be ``datetime.timedelta``.

        >>> total_seconds(timedelta(hours=2))
        7200

        or int:

        >>> total_seconds(100)
        100

        otherwise raise ``TypeError``.

        >>> total_seconds('100') # doctest: +ELLIPSIS
        Traceback (most recent call last):
            ...
        TypeError: ...
    """
    if isinstance(delta, int):
        return delta
    elif isinstance(delta, timedelta):
        return delta.seconds + delta.days * 86400
    else:
        raise TypeError('Expecting type datetime.timedelta '
                        'or int for seconds')


class utc(tzinfo):
    """ UTC timezone.

    """
    __slots__ = ('name')

    def __init__(self, name):
        self.name = name

    def tzname(self, dt):
        """ Name of time zone.

            >>> GMT.tzname(None)
            'GMT'
            >>> UTC.tzname(None)
            'UTC'
        """
        return self.name

    def utcoffset(self, dt):
        """ Offset from UTC.

            >>> UTC.utcoffset(None)
            datetime.timedelta(0)
        """
        return ZERO

    def dst(self, dt):
        """ DST is not in effect.

            >>> UTC.dst(None)
            datetime.timedelta(0)
        """
        return ZERO


GMT = utc('GMT')
UTC = utc('UTC')
