# -*- coding: utf-8 -*-
from nose import tools
from threading import Thread

from h10n.translator import Translator


def default_locale_test():
    """ h10n.translator.Translator: using default locale """
    locales = {'en-US': {}, 'ru-RU': {}}

    # Explicit setup of default locale
    translator = Translator(default='ru-RU', locales=locales)
    tools.eq_(translator.locale, 'ru-RU')

    # Implicit setup of default locale.  It must be random from available
    translator = Translator(locales=locales)
    tools.ok_(translator.locale in locales)


def maps_test():
    """ h10n.translator.Translator: using language and country maps """
    # Implicit map create
    translator = Translator(locales={'en-US': {}, 'ru-RU': {}})
    tools.eq_(translator.lang_map, {'en': 'en-US', 'ru': 'ru-RU'})
    tools.eq_(translator.country_map, {'US': 'en-US', 'RU': 'ru-RU'})

    # Lang property usage
    translator.lang = 'ru'
    tools.eq_(translator.lang, 'ru')
    tools.eq_(translator.country, 'RU')
    tools.eq_(translator.locale, 'ru-RU')

    # country property usage
    translator.country = 'US'
    tools.eq_(translator.lang, 'en')
    tools.eq_(translator.country, 'US')
    tools.eq_(translator.locale, 'en-US')

    # Merge implicitly created map items with explicitly ones
    translator = Translator(locales={'en-US': {}, 'en-GB': {},
                                     'ru-KZ': {}, 'kz-KZ': {}},
                            lang_map={'en': 'en-US'},
                            country_map={'KZ': 'ru-KZ'})
    tools.eq_(translator.lang_map,
              {'en': 'en-US', 'ru': 'ru-KZ', 'kz': 'kz-KZ'})
    tools.eq_(translator.country_map,
              {'US': 'en-US', 'GB': 'en-GB', 'KZ': 'ru-KZ'})


def use_only_test():
    """ h10n.translator.Translator: using use_only parameter """
    # As string
    translator = Translator(locales={'en-US': {}, 'ru-RU': {}},
                            use_only='ru-RU')
    tools.eq_(translator.locales.keys(), ['ru-RU'])

    # As comma-separated string
    translator = Translator(locales={'en-US': {}, 'ru-RU': {}},
                            use_only='ru-RU, en-US')
    tools.eq_(translator.locales.keys(), ['ru-RU', 'en-US'])

    # As list
    translator = Translator(locales={'en-US': {}, 'ru-RU': {}},
                            use_only=['ru-RU', 'en-US'])
    tools.eq_(translator.locales.keys(), ['ru-RU', 'en-US'])


def translate_test():
    """ h10n.translator.Translator: translate """
    translator = Translator(
        locales={
            'en-US': {
                'test': {
                    'message': 'Message',
                    'fallback': 'Fallback Message',
                }
            },
            'ru-RU': {
                'test': {
                    'message':  u'Сообщение',
                }
            }
        },
        fallback={'ru-RU': 'en-US', 'en-US': 'ru-RU'},
    )
    translator.locale = 'ru-RU'

    tools.eq_(translator.translate('test:message', 'Message'), u'Сообщение')
    tools.eq_(translator.translate('test:fallback', 'Fallback'),
              'Fallback Message')
    tools.eq_(translator.translate('test:invalid', 'Invalid Message'),
              'Invalid Message')


locales = {'en-US': {}, 'ru-RU': {}}
def scan_test():
    """ h10n.translator.Translator: using scan """
    # As string
    translator = Translator(
        scan='py://h10n.tests.translator_test.translator_test'
    )
    tools.eq_(translator.locales.keys(), locales.keys())

    # As comma-separated
    translator = Translator(
        scan='py://h10n.tests.translator_test.translator_test, '
             'py://h10n.tests.translator_test.translator_test:locales'
    )
    tools.eq_(translator.locales.keys(), locales.keys())

    # As list
    translator = Translator(
        scan=['py://h10n.tests.translator_test.translator_test']
    )
    tools.eq_(translator.locales.keys(), locales.keys())


def get_instance_test():
    """ h10n.translator.Translator: using registry """
    translator = Translator(name='registry_test', locales={'en-US': {}})
    tools.eq_(translator, Translator.get_instance('registry_test'))


def from_config_test():
    """ h10n.translator.Translator: using flat config """
    config = {
        'h10n.name': 'read_config_test',
        'h10n.locales.en-US.test.message': 'Message',
        'h10n.locales.en-US.[test.dotted.name].message': 'Message',
    }
    translator = Translator.from_config(config)
    tools.eq_(translator, Translator.get_instance('read_config_test'))
    tools.eq_(translator.translate('test:message', 'message'), 'Message')
    tools.eq_(translator.translate('test.dotted.name:message', 'message'),
              'Message')


def thread_local_strategy_test():
    """ h10n.translator.Translator: using thread_local strategy """
    translator = Translator(strategy='thread_local',
                            locales={'en-US': {}, 'ru-RU': {}})
    def worker():
        translator.locale = 'en-US'
    translator.locale = 'ru-RU'
    thread = Thread(target=worker)
    thread.start()
    thread.join()
    tools.eq_(translator.locale, 'ru-RU')


def helper_test():
    """ h10n.translator.Translator: using helpers """
    translator = Translator(
        locales={'en-US': {}, 'ru-RU': {}},
        helpers={'pluralize': 'h10n.helper.pluralize:Pluralize'}
    )
    translator.locale = 'en-US'
    tools.eq_(translator.helper.pluralize(1), 0)
    tools.eq_(translator.helper.pluralize(3), 1)
    tools.eq_(translator.helper.pluralize(5), 1)
    translator.locale = 'ru-RU'
    tools.eq_(translator.helper.pluralize(1), 0)
    tools.eq_(translator.helper.pluralize(3), 1)
    tools.eq_(translator.helper.pluralize(5), 2)
