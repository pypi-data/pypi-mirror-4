
""" ``introspection`` module.
"""

import warnings

from inspect import getargspec
from inspect import isfunction

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


class looks(object):
    """ Performs duck typing checks for two classes.

        Typical use::

            assert looks(IFoo, ignore_argspec=['pex']).like(Foo)
    """

    def __init__(self, cls):
        """
            *cls* - a class to be checked
        """
        self.cls = cls

    def like(self, cls, notice=None, ignore_funcs=None, ignore_argspec=None):
        """ Check if `self.cls` can be used as duck typing for `cls`.

            *cls* - class to be checked for duck typing.
            *ignore_funcs* - a list of functions to ignore
            *ignore_argspec* - a list of functions to ignore arguments spec.
        """
        notice = notice or []
        ignore_funcs = ignore_funcs or []
        ignore_argspec = ignore_argspec or []
        basis = declarations(cls, notice=notice)
        contestee = declarations(self.cls, notice=notice)
        for name in ignore_funcs:
            if name not in basis:
                warn("'%s': redundant ignore." % name)
                return False
        for name, t in basis.items():
            if name in ignore_funcs:
                continue
            if name not in contestee:
                warn("'%s': is missing." % name)
                return False
            else:
                t2 = contestee[name]
                if isfunction(t) and isfunction(t2):
                    if name in ignore_argspec:
                        continue
                    if getargspec(t) != getargspec(t2):
                        warn("'%s': argument names or defaults "
                             "have no match." % name)
                        return False
                elif t2.__class__ is not t.__class__:
                    warn("'%s': is not %s." % (name, t.__class__.__name__))
                    return False
        return True


# region: internal details

def declarations(cls, notice):
    return dict((name, t) for name, t in cls.__dict__.items()
                if name in notice or not name.startswith('_'))


def warn(message):
    warnings.warn(message, stacklevel=3)
