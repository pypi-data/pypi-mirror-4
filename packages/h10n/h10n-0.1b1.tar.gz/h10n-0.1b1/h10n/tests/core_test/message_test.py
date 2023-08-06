from nose import tools

from h10n.core import Message


def simple_test():
    """ h10n.core.Message: simple message """
    msg = Message(msg='Test Message')
    tools.eq_(msg.format(), 'Test Message')

def format_test():
    """ h10n.core.Message: using format """
    msg = Message(msg='a={a}, b={b}, c={c}', defaults={'a': 1, 'b': 2})
    tools.eq_(msg.format(b=3, c=3), 'a=1, b=3, c=3')

def properties_test():
    """ h10n.core.Message: using properties """
    msg = Message(property_1=1)
    tools.eq_(msg.property_1, 1)

def key_test():
    """ h10n.core.Message: using key """
    msg = Message(msg={'1': 'key=1', '2': 'key=2'}, key='{key}')
    tools.eq_(msg.format(key=1), 'key=1')
    tools.eq_(msg.format(key=2), 'key=2')

def filter_test():
    """ h10n.core.Message: using filter """
    msg = Message(msg='{b}', filter='$b = $a * self.factor', factor=2)
    tools.eq_(msg.format(a=10), '20')

def prototype_key_and_msg_test():
    """ h10n.core.Message: inherite prototype's key and msg """
    prototype = Message(msg={'1': 'key=1', '2': 'key=2'}, key='{key}')
    msg = Message(prototype=prototype)
    tools.eq_(msg.format(key=1), 'key=1')
    tools.eq_(msg.format(key=2), 'key=2')

def prototype_defaults_test():
    """ h10n.core.Message: inherite prototype's defaults """
    prototype = Message(defaults={'a': 1, 'b': 2})
    msg = Message(prototype=prototype, defaults={'b': 3, 'c': 3},
                  msg='a={a}, b={b}, c={c}')
    tools.eq_(msg.format(), 'a=1, b=3, c=3')

def prototype_properties_test():
    """ h10n.core.Message: inherite prototype's properties """
    prototype = Message(a=1, b=2)
    msg = Message(prototype=prototype, b=3, c=3)
    tools.eq_(msg.a, 1)
    tools.eq_(msg.b, 3)
    tools.eq_(msg.c, 3)

def prototype_filter_default_test():
    """ h10n.core.Message: inherite prototype's filter """
    prototype = Message(filter='$b = $a * self.factor', factor=2)
    msg = Message(prototype=prototype, msg='{b}', factor=3)
    tools.eq_(msg.format(a=10), '30')

def prototype_filter_extend_test():
    """ h10n.core.Message: extend prototype's filter """
    prototype = Message(filter='$b = $a * self.factor', factor=2)
    msg = Message(prototype=prototype, msg='{b}', factor=3, filter="""
        __prototype__
        $b += $c
    """)
    tools.eq_(msg.format(a=10, c=3), '33')

def passing_helper_test():
    """ h10n.core.Message: using helpers """
    helper = object()
    msg = Message(filter='$r = repr(helper)', msg='{r}', helper=helper)
    tools.eq_(msg.format(), repr(helper))
