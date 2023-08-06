#! /usr/bin/env python
"""
Decorators for cmt_convert package.
"""


def camel_case(text, sep=None):
    """
    Convert a string to camel case.

    :text: String to camel case
    """
    return ''.join(text.title().split(sep))


class Error(Exception):
    """
    Exceptions for this module.
    """
    pass


class DuplicateSymbolError(Error):
    """
    Error that indicates a symbol is already defined.
    """
    def __init__(self, symbol):
        self._symbol = symbol
        super(DuplicateSymbolError, self).__init__()

    def __str__(self):
        return self._symbol


class _ReaderPlugin(object):
    """
    Base class for reader plugins
    """
    def __init__(self):
        pass

    def __repr__(self):
        return '_ReaderPlugin ()'


class _WriterPlugin(object):
    """
    Base class for writer plugins
    """
    def __init__(self):
        pass

    def __repr__(self):
        return '_WriterPlugin ()'


class ReaderPlugin(object):
    """
    Decorator used to indicate that a function is intended to be a reader
    plugin.
    """
    def __init__(self, *args):
        if len(args) > 0:
            self.name = args[0]
        else:
            self.name = None

    def __call__(self, func):
        class_name = 'ReaderPlugin' + camel_case(func.__name__, sep='_')

        if self.name is None:
            self.name = func.__name__

        cls = type(class_name, (_ReaderPlugin, ),
                    dict(name=self.name,
                          description=(func.__doc__ or ''),
                          __name__=func.__name__,
                          __call__=func,
                         )
                   )
        globals()[class_name] = cls

        obj = cls()
        obj.func = func

        return obj


class WriterPlugin(object):
    """
    Decorator used to indicate that a function is intended to be a writer
    plugin.
    """
    def __init__(self, *args):
        if len(args) > 0:
            self.name = args[0]
        else:
            self.name = None

    def __call__(self, func):
        class_name = 'WriterPlugin' + camel_case(func.__name__, sep='_')

        if self.name is None:
            self.name = func.__name__

        cls = type(class_name, (_WriterPlugin, ),
                    dict(name=self.name,
                          description=(func.__doc__ or ''),
                          __name__=func.__name__,
                          __call__=func,
                         )
                   )
        #if globals().has_key(class_name):
        #    raise DuplicateSymbolError(class_name)
        globals()[class_name] = cls

        obj = cls()
        obj.func = func

        return obj
