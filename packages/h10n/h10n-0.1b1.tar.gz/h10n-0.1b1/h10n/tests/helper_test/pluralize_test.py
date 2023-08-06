from nose import tools

from h10n.helper.pluralize import Pluralize


def test():
    """ h10n.helper.pluralize: basic functional """
    pluralize = Pluralize('en', None)
    tools.eq_(pluralize(1), 0)
    tools.eq_(pluralize(3), 1)
    tools.eq_(pluralize(5), 1)

    pluralize = Pluralize('ru', None)
    tools.eq_(pluralize(1), 0)
    tools.eq_(pluralize(3), 1)
    tools.eq_(pluralize(5), 2)
