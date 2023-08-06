from nose import tools

from h10n.core import HelperNamespace

class FakeLocale(object):
    lang = 'en'
    country = 'US'
    name = 'en-US'

def base_test():
    """ h10n.core.HelperNamespace: basic functional """
    helper = HelperNamespace(
        FakeLocale(),
        {'pluralize': 'h10n.helper.pluralize:Pluralize'}
    )
    tools.eq_(helper.pluralize(1), 0)
    tools.eq_(helper.pluralize(2), 1)

def registry_test():
    """ h10n.core.HelperNamespace: using registry """
    helper_1 = HelperNamespace(
        FakeLocale(),
        {'pluralize': 'h10n.helper.pluralize:Pluralize'}
    )
    helper_2 = HelperNamespace(
        FakeLocale(),
        {'pluralize': 'h10n.helper.pluralize:Pluralize'}
    )
    tools.ok_(helper_1.pluralize is helper_2.pluralize)
