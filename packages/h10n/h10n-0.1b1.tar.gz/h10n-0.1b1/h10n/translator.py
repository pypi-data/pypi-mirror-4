import logging
import re

from h10n.core import Locale, HelperNamespace
from h10n.source import scanner


logger = logging.getLogger(__name__)


class Translator(object):
    """
    A Translator object is used to manage locales and perform translation.

    The Translator accepts a number of keyword arguments: ``name``, ``default``,
    ``locales``, ``use_only``, ``lang_map``, ``country_map``, ``fallback``,
    ``strategy``, ``scan`` and ``helpers``.

    If the ``name`` argument is passed as non-``None`` value, current instance
    of translator will be registered in the internal class-level registry.
    The *named* instance can be accessed later using :meth:`get_instance`
    class method.

    ..  warning::

        Attempt to initialize translator with name already in use will raise
        the ``ValueError``.

    The ``default`` argument, if passed, should be a name of default locale.

    The ``locales`` argument, if passed, should be a dictionary object,
    which store locale names in keys, and arguments for
    :class:`h10n.core.Locale` class in values.

    The ``use_only`` argument, if passed, should be a list of locale names,
    which will be used in the translator.  All other locales, passed via
    ``locales`` or loaded via ``scan``, will be ignored.

    The ``lang_map`` argument, if passed, should be a dictionary
    object, which store language names in keys, and locale names in values.
    The language map is used to resolve locale name via language name.
    The argument is needed only if you want to use :attr:`lang` property
    to manage locales and have more than one locale per language.
    For example, ``en-US`` and ``en-GB``.

    The ``country_map`` argument means the same thing as ``lang_map``,
    but is used to resolve locale via country name, i.e. :attr:`country` property.

    The ``fallback`` argument, if passed, should be a dictionary object,
    which store locale names in its keys and values.  Is used to resolve
    fallback order.

    The ``strategy`` argument means how to store name of current locale:
    globally and non-threadsafe (``simple``, default value) or locally in each
    thread (``thread_local`` value).

    The ``scan`` argument, if passed, should be a list of URIs to scan for
    locales.  All loaded locales will override the passed ones via ``locales``
    argument.

    The ``helpers`` argument, if passed, should be a dictionary, which store
    helper aliases in keys and python path's to helper factories in values.
    Is used to construct application-level helper namespace.
    """
    _instances = {}

    encoding = 'utf-8'

    def __init__(self, name=None,
                 default=None, locales=None, use_only=None,
                 lang_map=None, country_map=None,
                 fallback=None, strategy='simple', scan=None, helpers=None):
        if name is not None:
            if name in self.__class__._instances:
                raise ValueError('{0!r} already initialized'.format(
                                 self.__class__._instances[name]))
            self.__class__._instances[name] = self
        self.name = name
        self.default = default
        self.fallback = fallback or {}
        if strategy == 'simple':
            self.storage = _simple_storage()
        elif strategy == 'thread_local':
            self.storage = _thread_local_storage()
        else:
            raise ValueError('Invalid strategy "{0}"'.format(strategy))
        locales = locales or {}
        scan = _list(scan)
        use_only = _list(use_only)
        for source in scanner(scan):
            for name, catalogs in source.iteritems():
                locale = locales.setdefault(name, {})
                for catalog_name, catalog_properties in catalogs.iteritems():
                    if catalog_name in locale:
                        logger.warning('Overriding catalog %s:%s',
                                       name, catalog_name)
                    locale[catalog_name] = catalog_properties
        self.locales = {}
        self.lang_map = lang_map or {}
        self.country_map = country_map or {}
        for name, catalogs in locales.iteritems():
            if use_only and name not in use_only:
                continue
            locale = Locale(name, self, catalogs)
            self.locales[name] = locale
            if lang_map is None or locale.lang not in lang_map:
                self.lang_map[locale.lang] = name
            if country_map is None or locale.country not in country_map:
                self.country_map[locale.country] = name
        if self.default is None:
            self.default = self.locales.keys()[0]
        if helpers:
            for locale in self.locales.itervalues():
                locale.helper = HelperNamespace(locale, helpers)

    def __repr__(self):
        return 'Translator({0!r})'.format(self.name)

    @classmethod
    def get_instance(cls, name):
        """ Get a *named* instance from the registry:

        ..  code-block:: pycon

            >>> t = Translator(name='t', locales={'en-US': {}})
            >>> t is Translator.get_instance('t')
            True

        """
        if name not in cls._instances:
            cls._instances[name] = cls(name)
        return cls._instances[name]

    @classmethod
    def from_config(cls, config, prefix='h10n.'):
        """ Create Translator from "flat" configuration.

        A ``config`` argument should be a dictionary, which provide arguments
        for default constructor.  All nested dictionaries should be flatten
        using dot-separated keys.  The keys, which contain dots, should be
        escaped using square brackets.  If ``prefix`` argument is passed
        as non-empty string (default is ``h10n.``), all non-prefixed keys
        from ``config`` will be ignored.

        For example:

        ..  code-block:: pycon

            >>> # This...
            >>> Translator(locales={
            ...    'en-US': {
            ...        'test.catalog': {
            ...            'msg': u'Message'
            ...        }
            ...    }
            ... })
            Translator(None)

            >>> # ...is equal to:
            >>> Translator.from_config({
            ...     'h10n.locales.en-US.[test.catalog].msg':  u'Message'
            ... })
            Translator(None)


        """
        name_key = prefix + 'name'
        name = config.get(name_key)
        config_tree = {}
        prefix_len = len(prefix)
        dotted_name = re.compile('\[([\.\w\_]+)\]', re.I)
        for key, value in config.iteritems():
            if key == name_key:
                continue
            if key.startswith(prefix):
                key = key[prefix_len:]
                dotted_names = dotted_name.findall(key)
                if dotted_names:
                    dotted_names.reverse()
                    key = dotted_name.sub('###dotted_name###', key)
                path = key.split('.')
                last = path.pop()
                branch = config_tree
                for point in path:
                    if point == '###dotted_name###':
                        point = dotted_names.pop()
                    branch = branch.setdefault(point, {})
                branch[last] = value
        return cls(name=name, **config_tree)

    @property
    def locale(self):
        """ Set or get current locale name """
        return self.storage.__dict__.get('locale', self.default)

    @locale.setter
    def locale(self, locale):
        if locale not in self.locales:
            raise ValueError('Unsupported locale "{0}"'.format(locale))
        self.storage.locale = locale

    @property
    def lang(self):
        """ Set or get current locale name using language part of the name """
        return self.locales[self.locale].lang

    @lang.setter
    def lang(self, lang):
        if lang not in self.lang_map:
            raise ValueError('Unsupported lang "{0}"'.format(lang))
        self.locale = self.lang_map[lang]

    @property
    def country(self):
        """ Set or get current locale name using country part of the name """
        return self.locales[self.locale].country

    @country.setter
    def country(self, country):
        if country not in self.country_map:
            raise ValueError('Unsupported country "{0}"'.format(country))
        self.locale = self.country_map[country]

    @property
    def helper(self):
        """ Get application-level helper namespace from current locale """
        return self.locales[self.locale].helper

    def translate(self, id, fallback, locale=None, **params):
        """ Perform message translation

        An ``id`` argument should be an identifier of the message to translate,
        i.e. string in format ``{catalog}:{message}``.

        A ``fallback`` argument should be a string, which will be used as
        result of failed translation.

        A ``locale`` argument, if passed as non-``None`` value, should be a name
        of locale, which override current one on translation time.

        Other keyword arguments will be passed directly to
        :meth:`h10n.core.Message.format` method.
        """
        failed_locales = []
        locale = locale or self.locale
        logger.debug('Translate %s:%s', locale, id)
        while True:
            try:
                return self.locales[locale][id].format(**params)
            except Exception:
                logger.error('Translation error %s:%s',
                             locale, id, exc_info=True)
                failed_locales.append(locale)
                fallback_locale = self.fallback.get(locale, self.default)
                if not fallback_locale or fallback_locale in failed_locales:
                    break
                locale = fallback_locale
                logger.debug('Fallback to %s', locale)
        return fallback

    def message(self, id, fallback=None, **params):
        """
        Factory for lazy translatable messages.  Creates :class:`Message` object
        using ``self`` as ``translator`` argument.
        """
        return Message(self, id, fallback, **params)


class Message(object):
    """
    A Message object is used for lazy translatable messages.

    A ``translator`` argument must be an instance or name of instance of
    :class:`Translator` class.  All other arguments are the same as for
    :meth:`Translator.translate` method.

    The Message object will be translated implicitly on convert into
    ``unicode`` or ``str``.  It also can be called to be translated explicitly.
    Keyword arguments passed via ``__call__`` method will override passed ones
    via constructor.
    """

    def __init__(self, translator, id, fallback, **params):
        if isinstance(translator, basestring):
            translator = Translator.get_instance(translator)
        self.translator = translator
        self.id = id
        self.fallback = fallback
        self.params = params

    def __call__(self, **params):
        if params:
            p = self.params.copy()
            p.update(params)
            params = p
        else:
            params = self.params
        return self.translator.translate(self.id, self.fallback, **params)

    def __repr__(self):
        return '<Message: {0}>'.format(self.id)

    def __unicode__(self):
        return self.translator.translate(self.id, self.fallback, **self.params)

    def __str__(self):
        return unicode(self).encode(self.translator.encoding)

    def __mod__(self, right):
        return unicode(self) % right


from threading import local as _thread_local_storage
class _simple_storage(object): pass

def _list(value):
    if value is None:
        value = []
    if isinstance(value, basestring):
        value = [item.strip() for item in value.split(',')]
    return value
