from nose import tools

from h10n.core import Locale, Catalog, Message


def test():
    """ h10n.core.Locale: basic functional """
    locale = Locale('xx-YY', catalogs={
        'catalog': {'message': 'Message'}
    })
    catalog = locale['catalog']
    message = locale['catalog:message']

    tools.eq_(locale.name, 'xx-YY')
    tools.eq_(locale.lang, 'xx')
    tools.eq_(locale.country, 'YY')
    tools.ok_(isinstance(catalog, Catalog))
    tools.ok_(isinstance(message, Message))
    tools.eq_(catalog.name, 'catalog')
    tools.eq_(message.name, 'message')
