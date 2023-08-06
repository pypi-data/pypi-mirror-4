
""" ``json`` module.
"""

from decimal import Decimal

from wheezy.core.comp import SimpleJSONEncoder
from wheezy.core.comp import json_dumps
from wheezy.core.comp import json_loads
from wheezy.core.comp import str_type
from wheezy.core.datetime import format_iso_datetime
from wheezy.core.datetime import format_iso_time
from wheezy.core.introspection import import_name

date = import_name('datetime.date')
datetime = import_name('datetime.datetime')
time = import_name('datetime.time')


def json_encode(obj):
    """ Encode ``obj`` as a JSON formatted unicode string.

        Correctly escapes forward slash to be able
        embed javascript code.
    """
    return json_dumps(obj, cls=JSONEncoder, ensure_ascii=False,
                      separators=(',', ':')).replace('</', '<\\/')


def json_decode(s):
    """ Decode ``s`` (containing a JSON unicode string) to a Python
        object.
    """
    return json_loads(s, parse_float=Decimal)


class JSONEncoder(SimpleJSONEncoder):

    def default(self, obj):
        if isinstance(obj, datetime):
            if obj == datetime.min:
                return str_type('')
            return format_iso_datetime(obj)
        elif isinstance(obj, date):
            if obj == date.min:
                return str_type('')
            return obj.isoformat()
        elif isinstance(obj, time):
            return format_iso_time(obj)
        elif isinstance(obj, Decimal):
            return str_type(obj)
        else:  # pragma: nocover
            return super(JSONEncoder, self).default(obj)
