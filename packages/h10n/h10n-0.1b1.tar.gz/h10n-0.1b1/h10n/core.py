"""
A Core module contains objects which is used by h10n internally.  End users
don't need to use this module directly.
"""

import re
import pkg_resources
from textwrap import dedent
from threading import RLock

from h10n.util import keep_context
from h10n.util import NamedObject, Namespace


class Locale(NamedObject):
    """
    A Locale object is used to store translation catalogs.  The locale accepts
    three arguments: ``name``, ``translator`` and ``catalogs``.

    The ``name`` argument should be a locale name in format ``xx-YY``, where
    ``xx`` is language code and ``YY`` is country code.  Name itself, language
    and country codes can be accessed via ``name``, ``lang`` and ``country``
    attributes of the Locale object.

    The ``translator`` argument should be an instance of
    :class:`h10n.translator.Translator` class, which own current locale.
    Locale itself doesn't use ``translator``, but it can be useful in the
    filters of :class:`Message` objects.

    The ``catalogs`` argument should be a dictionary object, which store catalog
    names in keys and arguments for :class:`Catalog` class in values.

    Messages can be accessed using subscription interface.  It can be accessed
    directly using key in format ``{catalog}:{message}`` or via catalog:

    ..  code-block:: pycon

        >>> l = Locale('en-US', None, {'test': {'message': u'Message'}})
        >>> l['test']
        <Catalog: test>
        >>> l['test:message']
        <Message: message>
        >>> l['test:message'] is l['test']['message']
        True

    """

    @keep_context
    def __init__(self, name, translator=None, catalogs=None):
        self.name = name
        self.translator = translator
        self.lang, self.country = name.split('-')
        self.catalogs = {}
        for catalog_name, catalog in catalogs.iteritems():
            self.catalogs[catalog_name] = Catalog(catalog_name, self, catalog)

    @keep_context
    def __getitem__(self, name):
        if ':' in name:
            name, tail = name.split(':', 1)
            return self.catalogs[name][tail]
        return self.catalogs[name]


class Catalog(NamedObject):
    """
    A Catalog object is used to extract :class:`Message` objects from sources,
    group it in the :class:`Locale` and provide :class:`HelperNamespace` object
    for message's filters.  The Catalog accepts three arguments: ``name``,
    ``locale`` and ``config``.

    The ``name`` argument is catalog name, as it defined in :class:`Locale`.
    Is used for debugging only.

    The ``locale`` argument should be an instance of :class:`Locale` class,
    which own this catalog.  Is used to create helper namespace and messages.

    The ``config`` arguments should be a dictionary.  If the dictionary contain
    callable object under the key ``factory``, this object becomes factory of
    message source and all other values of the dictionary are passed as keyword
    arguments to this factory.  Otherwise, ``config`` itself becomes message
    source.

    The message source should be a dictionary-like object, which provides two
    methods ``__getitem__`` and ``__setitem__``.  First one should return
    message definition or instance of :class:`Message` class.  Second one
    should accept instance of :class:`Message` to store it in cache.  See
    :mod:`h10n.source` doc-string to learn more about message sources.

    The message definition should be a string or dictionary.  If it passed as
    string, it is converted to dictionary ``{'msg': 'passed string'}``.
    Dictionary should contain keyword arguments to :class:`Message` constructor.

    When message is requested, using subscription interface, catalog redirects
    request to the message source.  If source return instance of
    :class:`Message`, this instance is returned as is.  If source return
    message definition, catalog extracts message prototype from locale,
    creates :class:`Message` object, put it into source and return it as result.

    Example:

    ..  code-block:: pycon

        >>> source_1 = {'prototype': 'test 1'}
        >>> source_2 = {'test': {'prototype': 'source_1:prototype'}}
        >>> locale = Locale('en-US', None, {'source_1': source_1,
        ...                                 'source_2': source_2})
        >>> locale['source_2:test']
        <Message: test>
        >>> source_1
        {'prototype': <Message: prototype>}
        >>> source_2
        {'test': <Message: test>}
    """

    @keep_context
    def __init__(self, name, locale, config):
        self.name = name
        self.locale = locale
        self._mutex = RLock()
        if 'factory' in config and callable(config['factory']):
            factory = config.pop('factory', None)
            self.source = factory(**config)
        else:
            self.source = config
        try:
            self.helper = HelperNamespace(self.locale,
                                          self.source['__helper__'])
        except KeyError:
            self.helper = None

    @keep_context
    def __getitem__(self, name):
        message = self.source[name]
        if not isinstance(message, Message):
            with self._mutex:
                if isinstance(message, basestring):
                    message = {'msg': message}
                else:
                    message = message.copy()
                if message.get('prototype'):
                    message['prototype'] = self.locale[message['prototype']]
                message = self.source[name] = Message(name, self.locale,
                                                      helper=self.helper,
                                                      **message)
        return message


class Message(NamedObject, Namespace):
    """
    A Message object store translation strings, associated metadata
    and formatting filter.

    The Message accepts a number of keyword arguments: ``name``, ``locale``,
    ``prototype``, ``key``, ``msg``, ``defaults``, ``filter`` and ``helper``.

    The ``name`` argument is a name of the message, as it specified in
    :class:`Catalog`.  Is used for debugging only.

    The ``locale`` argument should be an instance of :class:`Locale` class.
    Is used in filter only and can be accessed via ``locale`` attribute.

    The ``prototype`` argument should be an instance of this class.  If it is
    passed as non-``None`` value, current instance will inherit from prototype
    metadata and formatting filter.

    The ``key`` argument is a template for key, which is used to choose
    appropriate translation string from ``msg``, when it passed as dictionary.

    The ``msg`` argument is a translation string itself.  If is passed as
    dictionary object, the ``key`` argument is required.

    The ``defaults`` argument should be a dictionary with default parameters,
    which will be used in the :meth:`format` method.

    The ``filter`` argument is a string of code, which is compiled into filter
    function.  The code is a regular Python code with a pinch of syntax sugar.
    There are the rules of how the ``filter`` argument become a function:

    1.  The code is prepended by ``def filter(self, kw):``.
    2.  Dollar-prefixed names is transformed to keys of ``kw``, i.e.
        ``$name`` -> ``kw["name"]``.
    3.  ``__prototype__`` string is transformed to call of prototype's filter,
        i.e. ``self.prototype.filter(self, kw)``.
    4.  The result code is executed with the ``helper`` argument in the local
        namespace.

    The ``helper`` is a :class:`HelperNamespace` object, which will be available
    in the filter as global name.

    Example:

    ..  code-block:: pycon

        >>> locale = Locale('en-US', None, {})
        >>> helper = {'pluralize': 'h10n.helper.pluralize:Pluralize'}
        >>> helper = HelperNamespace(locale, helper)
        >>> prototype = Message(key='{form}',
        ...                     defaults={'count': 1},
        ...                     filter='$form = helper.pluralize($count)',
        ...                     helper=helper)
        >>> message = Message(msg={'0': u'{count} item',
        ...                        '1': u'{count} items'},
        ...                   prototype=prototype)
        >>> message.format()
        u'1 item'
        >>> message.format(count=3)
        u'3 items'

    """

    _parser = re.compile('\$([a-z_]{1}[a-z_0-9]*)', re.I)

    @keep_context
    def __init__(self, name='__empty__', locale=None, prototype=None,
                 key=None, msg=None, defaults=None, filter=None, helper=None,
                 **properties):
        self.name = name
        self.locale = locale
        self.key = key
        self.msg = msg
        self.filter = None
        self.defaults = {}
        self.prototype = prototype
        self.freeze()
        if self.prototype:
            self.key = self.key or self.prototype.key
            self.msg = self.msg or self.prototype.msg
            self.defaults.update(self.prototype.defaults)
            self.extend(self.prototype)
        self.defaults.update(defaults or {})
        self.extend(properties)
        if filter is None and self.prototype and self.prototype.filter:
            filter = '__prototype__'
        if filter:
            filter = dedent(filter)
            if '__prototype__' in filter:
                if self.prototype and self.prototype.filter:
                    prototype_call = 'self.prototype.filter(self, kw)'
                else:
                    prototype_call = ''
                filter = filter.replace('__prototype__', prototype_call)
            filter = self._parser.sub(r'kw["\g<1>"]', filter)
            filter = filter.split('\n')
            filter.insert(0, 'def filter(self, kw):')
            filter = '\n    '.join(filter)
            exec filter in {'self': self, 'helper': helper}, self.__dict__

    @keep_context
    def format(self, **kw):
        """
        Format translation string according to passed parameters.

        Formatting is performed in following steps:

        1.  Merge passed parameters with default ones.
        2.  Pass parameters to ``filter``.
        3.  Format ``key``, if it is not ``None``.
        4.  Choose translation string from ``msg``, if ``msg`` is dictionary,
            or use ``msg`` as translation string.
        5.  Format translation string and return result.

        Formatting ``key`` and ``msg`` (translation string) is performed using
        standard ``format`` method of ``str`` and ``unicode`` objects.
        See `PEP 3101`_ for details.

        .. _`PEP 3101`: http://www.python.org/dev/peps/pep-3101/
        """
        params = self.defaults.copy()
        params.update(kw)
        if self.filter:
            self.filter(self, params)
        msg = self.msg
        if self.key is not None:
            key = self.key.format(**params)
            msg = msg[key]
        return msg.format(**params)


class HelperNamespace(Namespace):
    """
    A Helper Namespace object is used to store helpers in the :class:`Locale`
    (actually are created by :class:`h10n.translator.Translator` and named
    "application-level helpers") and :class:`Catalog` objects.

    The Helper Namespace accepts two arguments: ``locale`` and ``helpers``.

    The ``locale`` argument should be an instance of :class:`Locale` class.

    The ``helpers`` argument should be a dictionary, which store helper aliases
    in its keys and helper specifications in its values.  The alias become
    helper name in the namespace.  The specification should be a Python path
    to the helper factory, similar to path using in the entry points from
    `pkg_resources`_, i.e. ``python.path.to.helper.module:HelperFactory``.

    .. _`pkg_resources`: http://packages.python.org/distribute/pkg_resources.html

    Each helper and locale pair is registered in the internal class-level
    registry.  This mean, that two different Helper Namespace objects with
    similar locale and helper specification use shared helper object, instead
    of create diffrent objects for each instance of the namespace.

    See :class:`h10n.helper.pluralize.Pluralize` as helper example.

        >>> locale = Locale('en-US', None, {})
        >>> helpers = {'pluralize': 'h10n.helper.pluralize:Pluralize'}
        >>> h = HelperNamespace(locale, helpers)
        >>> h.pluralize                                  # doctest: +ELLIPSIS
        <h10n.helper.pluralize.Pluralize object at ...>
        >>> h2 = HelperNamespace(locale, helpers)
        >>> h.pluralize is h2.pluralize
        True
    """

    _registry = {}

    def __init__(self, locale, helpers):
        properties = {}
        cls = self.__class__
        for alias, helper in helpers.iteritems():
            if (locale.name, helper) not in cls._registry:
                entry_point = 'x={0}'.format(helper)
                entry_point = pkg_resources.EntryPoint.parse(entry_point)
                factory = entry_point.load(False)
                cls._registry[locale.name, helper] = factory(locale.lang,
                                                             locale.country)
            properties[alias] = cls._registry[locale.name, helper]
        self.extend(properties)
