# -*- coding: utf-8 -*-
from nose import tools

from h10n.translator import Translator, Message


def setup():
    Translator(
        name='message_test',
        locales={
            'en-US': {
                'test': {
                    'message': 'Message',
                }
            },
            'ru-RU': {
                'test': {
                    'message':  u'Сообщение',
                }
            }
        },
        default='en-US',
    )


def instance_via_translator_test():
    """ h10n.translator.Message: instance via Translator """
    translator = Translator.get_instance('message_test')
    message = translator.message('test:message', 'message')

    translator.locale = 'en-US'
    tools.eq_(unicode(message), 'Message')

    translator.locale = 'ru-RU'
    tools.eq_(unicode(message), u'Сообщение')


def direct_instance_test():
    """ h10n.translator.Message: direct instance """
    translator = Translator.get_instance('message_test')
    message_1 = Message(translator, 'test:message', 'message')
    message_2 = Message('message_test', 'test:message', 'message')

    translator.locale = 'en-US'
    tools.eq_(unicode(message_1), 'Message')
    tools.eq_(unicode(message_2), 'Message')

    translator.locale = 'ru-RU'
    tools.eq_(unicode(message_1), u'Сообщение')
    tools.eq_(unicode(message_2), u'Сообщение')
