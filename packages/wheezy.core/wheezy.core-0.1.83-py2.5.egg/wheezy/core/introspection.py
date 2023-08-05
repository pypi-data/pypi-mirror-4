
""" ``introspection`` module.
"""

import warnings

from inspect import getargspec
from inspect import isclass
from inspect import isfunction

from wheezy.core.comp import __import__
from wheezy.core.descriptors import attribute


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

    def __init__(self, cls, ignore_funcs=None, ignore_argspec=None):
        """
            *cls* - a class to be checked
            *ignore_funcs* - a list of functions to ignore
            *ignore_argspec* - a list of functions to ignore arguments spec.
        """
        self.declarations = declarations(cls)
        self.ignore_funcs = ignore_funcs or []
        self.ignore_argspec = ignore_argspec or []

    def like(self, cls):
        """ Check if `self.cls` can be used as duck typing for `cls`.

            *cls* - class to be checked for duck typing.
        """
        for n, t in declarations(cls).items():
            if n in self.ignore_funcs:
                continue
            if n not in self.declarations:
                warn("'%s': is missing." % n)
                return False
            else:
                t2 = self.declarations[n]
                if isfunction(t) and isfunction(t2):
                    if n in self.ignore_argspec:
                        continue
                    if getargspec(t) != getargspec(t2):
                        warn("'%s': argument names or defaults "
                             "have no match." % n)
                        return False
                elif t2.__class__ is not t.__class__:
                    warn("'%s': is not %s." % (n, t.__class__.__name__))
                    return False
        return True


# region: internal details

def declarations(cls):
    return dict((n, v) for n, v in cls.__dict__.items()
                if not n.startswith('_'))


def warn(message):
    warnings.warn(message, stacklevel=3)
