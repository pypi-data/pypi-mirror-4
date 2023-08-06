"""
A Source module is used to process different types of message sources.

There are two global variable in the module: ``file_sources`` and ``scanners``.

The ``file_sources`` variable is used by :func:`scan_path` to determine
supported file types.  It is a dictionary, which contain file extensions
(prefixed by dot char) in its keys and file source factories in its values.
This dictionary is filled on import time using entry points from
``h10n.source.file`` group.  The entry point name is used as file extension.
h10n support only YAML-files out of the box, but you can add another ones using
entry points.

..  code-block:: pycon

    >>> file_sources['.yaml']
    <class 'h10n.source.YAMLSource'>
    >>> file_sources['.yaml'] is file_sources['.yml']
    True


The ``scanners`` variable is used by :func:`scanner` function to determine
supported types of scanners.  It is a dictionary, which contain protocol name
of scanner in its keys, and scanners in its values.  This dictionary is filled
on import time using entry points from ``h10n.scanner`` group.  The entry point
name is used as protocol name.

..  code-block:: pycon

    >>> scanners['path']                                # doctest: +ELLIPSIS
    <function scan_path at ...>
    >>> scanners['asset']                               # doctest: +ELLIPSIS
    <function scan_asset at ...>
    >>> scanners['py']                                  # doctest: +ELLIPSIS
    <function scan_py at ...>

"""

import os
import re
import pkg_resources
import yaml
import logging


logger = logging.getLogger(__name__)


class YAMLSource(dict):
    """ A message source, which extracts message definitions from YAML-files """
    def __init__(self, path):
        with open(path) as f:
            self.update(yaml.load(f))


def scanner(uri_list):
    """
    A scanner is used to build locale definitions by scanning specified URIs.

    The scanner accepts single argument -- URI list, and returns an iterator
    over scanning result of each URI.

    URI's protocol is used to determine how to scan particular URI.  It must be
    a key from the ``scanners`` dictionary from this module.  For example,
    URI ``asset://myapp.resources:translations`` will be scanned
    by :func:`scan_asset`.
    """
    for uri in uri_list:
        protocol, spec = uri.split('://')
        try:
            yield scanners[protocol](spec)
        except KeyError:
            raise ValueError('Unknown scanner "{0}"'.format(protocol))


def scan_py(spec):
    """
    A scanner of Python modules extracts locale definitions from source code
    directly.  Accepts ``spec`` argument, which should be a string in format
    ``modlule.name:locale_definitions``.  If definition part is empty, i.e.
    ``spec`` is passed as ``module.name``, name ``locales`` is used by default.
    So, ``module.name`` is equal to ``module.name:locales``.
    """
    if ':' not in spec:
        spec += ':locales'
    return pkg_resources.EntryPoint.parse('x={0}'.format(spec)).load(False)


def scan_asset(spec):
    """
    A scanner of Python package assets works the same way as scanner of file
    system.  See :func:`scan_path` doc-string for details.  Asset specification
    should be in format ``package.name:asset/path``, where ``asset/path`` is
    a path, relative to ``package.name`` package path.
    """
    if ':' in spec:
        package, dir = spec.split(':')
    else:
        package, dir = spec, ''
    path = pkg_resources.resource_filename(package, dir)
    return scan_path(path)


def scan_path(base_path):
    """
    A scanner of file system extracts locale definitions from directory path.
    The directory should contain subdirectories, which should be named
    as locale, using format ``xx-YY`` (all other will be skipped).
    Each subdirectory is scanned recursively.  Each supported file is used for
    message catalog, where catalog name is equal to file name without extension
    relative to locale directory with slashes replaced by dots, i.e.
    file ``en-US/common/objects.yaml`` will be used as source for catalog
    ``common.objects`` in locale ``en-US``.  Supported files are detected
    according its extension, using registry of file sources -- global variable
    from this module ``file_sources``.
    """
    if not os.path.isdir(base_path):
        raise ValueError("Can't to scan path {0}".format(base_path))
    result = {}
    locale_pattern = re.compile(r'[a-z]{2}\-[A-Z]{2}')
    for locale_name in os.listdir(base_path):
        locale_path = os.path.join(base_path, locale_name)
        if not (os.path.isdir(locale_path) and
                locale_pattern.match(locale_name)):
            continue
        locale = result[locale_name] = {}
        for path, dirs, files in os.walk(locale_path):
            for name in files:
                if name[0] in ('.', '_'):
                    continue
                file_path = os.path.join(path, name)
                full_name = os.path.relpath(file_path, locale_path)
                name, ext = os.path.splitext(full_name)
                ext = ext.lower()
                if ext not in file_sources:
                    logger.info('Unsupported file type "{0}"; skipped'.
                                format(file_path))
                    continue
                name = name.replace(os.path.sep, '.')
                locale[name] = {
                    'factory': file_sources[ext],
                    'path': file_path,
                }
            # Skip directories which names starts with '.' or '_'
            for name in dirs[:]:
                if name[0] in ('.', '_'):
                    dirs.remove(name)
    return result


file_sources = {}
for entry_point in pkg_resources.iter_entry_points('h10n.source.file'):
    file_sources[entry_point.name] = entry_point.load()

scanners = {}
for entry_point in pkg_resources.iter_entry_points('h10n.scanner'):
    scanners[entry_point.name] = entry_point.load()
