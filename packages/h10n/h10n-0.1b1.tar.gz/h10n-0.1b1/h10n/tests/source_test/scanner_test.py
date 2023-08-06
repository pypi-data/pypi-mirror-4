import os
from nose import tools

from h10n.source import scanner, scan_py, scan_path, scan_asset
from h10n.source import YAMLSource

path = os.path.join(os.path.dirname(__file__), 'assets')
locales = {
    'en-US': {
        'source': {
            'factory': YAMLSource,
            'path': os.path.join(path, 'en-US', 'source.yaml')
        },
        'nested.source': {
            'factory': YAMLSource,
            'path': os.path.join(path, 'en-US', 'nested', 'source.yaml')
        },
    }
}

def scan_py_test():
    """ h10n.source.scan_py: scan python modules """
    # Implicit form
    result = scan_py('h10n.tests.source_test.scanner_test')
    tools.eq_(result, locales)
    # Explicit form
    result = scan_py('h10n.tests.source_test.scanner_test:locales')
    tools.eq_(result, locales)

def scan_path_test():
    """ h10n.source.scan_path: scan path in filesystem """
    result = scan_path(path)
    tools.eq_(result, locales)

def scan_asset_test():
    """ h10n.source.scan_asset: scan python package assets """
    result = scan_asset('h10n.tests.source_test:assets')
    tools.eq_(result, locales)

def scanner_test():
    """ h10n.source.scanner: complex scan """
    scan = ['py://h10n.tests.source_test.scanner_test',
            'path://{0}'.format(path),
            'asset://h10n.tests.source_test:assets']
    result = list(scanner(scan))
    tools.eq_(result[0], locales)
    tools.eq_(result[1], locales)
    tools.eq_(result[2], locales)
