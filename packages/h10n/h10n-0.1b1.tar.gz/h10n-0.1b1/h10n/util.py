"""
An Utility module contains objects which is used by h10n internally.  End users
don't need to use this module directly.
"""


class Namespace(object):
    """
    Namespace is an utility object, which mimics to JavaScript object.
    The Namespace provides methods to manipulate attributes using subscription
    interface:

    ..  code-block:: pycon

        >>> ns = Namespace()
        >>> ns.a = 1
        >>> ns['a']
        1
        >>> ns['a'] = 2
        >>> ns.a
        2
        >>> ns['b.c'] = 3
        >>> ns.b.c
        3
        >>> ns.b                                     # doctest: +ELLIPSIS
        <h10n.util.Namespace object at ...>

    """

    _frozen = ()

    def extend(self, d):
        """
        Extends namespace by attributes from dictionary or another namespace.
        Dot-separated keys in the dictionary becomes to nested namespace.

        ..  code-block:: pycon

            >>> ns = Namespace().extend({'a.b': 1, 'c': 2})
            >>> ns.a.b
            1
            >>> ns.c
            2
            >>> ns.a                                 # doctest: +ELLIPSIS
            <h10n.util.Namespace object at ...>
            >>> ns_2 = Namespace().extend({'c': 3, 'd': 4, 'a.e': 5})
            >>> ns.extend(ns_2)                      # doctest: +ELLIPSIS
            <h10n.util.Namespace object at ...>
            >>> ns.c
            3
            >>> ns.d
            4
            >>> ns.a.e
            5

        """
        for name, value in d.iteritems():
            if name.startswith('_') or name in self._frozen:
                continue
            self[name] = value
        return self

    def freeze(self):
        """
        Freeze current attributes of namespace to prevent overriding via extend.

        ..  code-block:: pycon

            >>> ns = Namespace().extend({'a': 1})
            >>> ns.freeze()
            >>> ns.extend({'a': 2}).a
            1

        """
        self._frozen = [name for name in dir(self) if not name.startswith('_')]

    def __getitem__(self, name):
        if '.' in name:
            try:
                name, tail = name.split('.', 1)
                return self.__dict__[name][tail]
            except KeyError:
                # Raise another KeyError to store proper key as argument
                raise KeyError(name)
        return self.__dict__[name]

    def __setitem__(self, name, value):
        if '.' in name:
            name, tail = name.split('.', 1)
            if name not in self.__dict__ or \
               not isinstance(self.__dict__[name], Namespace):
                self.__dict__[name] = Namespace()
            self.__dict__[name][tail] = value
        else:
            self.__dict__[name] = value

    def get(self, name, default=None):
        try:
            return self[name]
        except KeyError:
            return default

    def iteritems(self):
        for name, value in self.__dict__.iteritems():
            if isinstance(value, Namespace):
                for subname, subvalue in value.iteritems():
                    yield '{0}.{1}'.format(name, subname), subvalue
            else:
                yield name, value


class NamedObject(object):
    """
    An utility base class for named objects, which is used in the exception
    context.  See :class:`ExceptionContext` doc-strings.

    ..  code-block:: pycon

        >>> no = NamedObject()
        >>> no
        <NamedObject: __empty__>
        >>> no.name = 'test'
        >>> no
        <NamedObject: test>

    """

    name = '__empty__'

    def __repr__(self):
        return '<{0}: {1}>'.format(self.__class__.__name__, self.name)


class ExceptionContext(NamedObject):
    """
    An Exception Context is utility object to store context in the exception
    arguments.  The Exception Context is used via :func:`keep_context`
    decorator.
    """

    def __init__(self, obj):
        self.chain = [obj]

    @property
    def name(self):
        return repr(self.chain)

    @classmethod
    def extend(cls, exception, obj):
        """ Extends existent context of exception or add new one """
        # Search for existent context in exception arguments
        for arg in reversed(exception.args):
            if isinstance(arg, cls):
                if obj not in arg.chain:
                    arg.chain.insert(0, obj)
                raise
        # Create new context and add it to the end of exception's arguments
        exception.args += (cls(obj),)
        raise


def keep_context(method):
    """
    Includes context into exception raised from decorated method.

    ..  code-block:: pycon

        >>> class Test(NamedObject):
        ...     def __init__(self, name):
        ...         self.name = name
        ...     @keep_context
        ...     def test(self):
        ...         raise Exception('Test exception')
        >>> Test('foo').test()
        Traceback (most recent call last):
        ...
        Exception: ('Test exception', <ExceptionContext: [<Test: foo>]>)

    """
    def context_keeper(self, *args, **kwargs):
        try:
            return method(self, *args, **kwargs)
        except Exception, e:
            ExceptionContext.extend(e, self)
    context_keeper.__name__ = method.__name__
    context_keeper.__doc__ = method.__doc__
    return context_keeper
