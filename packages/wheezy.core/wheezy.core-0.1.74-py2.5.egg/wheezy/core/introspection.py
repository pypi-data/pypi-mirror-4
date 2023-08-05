
""" ``introspection`` module.
"""

from wheezy.core.comp import __import__


def import_name(fullname):
    """ Dynamically imports object by its full name.

        >>> from datetime import timedelta
        >>> import_name('datetime.timedelta') is timedelta
        True
    """
    namespace, name = fullname.rsplit('.', 1)
    obj = __import__(namespace, None, None, [name])
    return getattr(obj, name)
