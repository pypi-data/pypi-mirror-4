
""" ``config`` module.
"""

DEBUG = False


class Config(object):
    """ Promotes ``options`` dict to attributes. If an option
        can not be found in ``options`` tries to get it from
        ``master``. ``master`` must have a requested option
        otherwise raises error.

        ``master`` can be a module.

        >>> from sys import modules
        >>> m = modules[Config.__module__]
        >>> c = Config(master=m)
        >>> c.DEBUG
        False

        or an instance of ``dict``.

        >>> c = Config(master={'DEBUG': False})
        >>> c.DEBUG
        False

        ``options`` override ``master``.

        >>> c = Config(options={'DEBUG': True}, master=m)
        >>> c.DEBUG
        True

        If option is not defined it takes from ``master``.

        >>> c = Config(master=m)
        >>> c.DEBUG
        False

        Configs can be nested

        >>> m = Config(dict(B='b'))
        >>> c = Config(dict(A='a'), master=m)
        >>> c.B
        'b'

        if ``options`` is an instance of ``Config`` than use
        its options only so this config can have own master.

        >>> options = Config(dict(A='a'))
        >>> c = Config(options)
        >>> c.A
        'a'
    """

    def __init__(self, options=None, master=None):
        if isinstance(options, Config):
            self.options = options.options
        else:
            self.options = options or {}
        if master:
            if isinstance(master, dict):
                self.get_master = lambda n: master[n]
            else:
                self.get_master = lambda n: getattr(master, n)
        else:
            self.get_master = lambda n: None

    def __getattr__(self, name):
        if name in self.options:
            val = self.options[name]
        else:
            val = self.get_master(name)
        setattr(self, name, val)
        return val
