import os.path
import re
import sys

from distutils.core import setup


class Mock(object):
    def __init__(self, *args, **kwargs):
        pass

    def __call__(self, *args, **kwargs):
        return Mock()

    @classmethod
    def __getattr__(cls, name):
        if name in ('__file__', '__path__'):
            return '/dev/null'
        elif name[0] == name[0].upper():
            mockType = type(name, (), {})
            mockType.__module__ = __name__
            return mockType
        else:
            return Mock()

MOCK_MODULES = ['anyjson', 'httplib2']
for mod_name in MOCK_MODULES:
    sys.modules[mod_name] = Mock()

def pep386(v):
    regex = re.compile(r' (?:([ab])\w+) (\d+)$')
    if regex.search(v):
        base = regex.sub('', v)
        minor = ''.join(regex.search(v).groups())
        return base + minor
    return v

version = __import__("auspost").__version__

if __name__ == '__main__':
    README = os.path.join(os.path.dirname(__file__), 'README.txt')
    setup(
        name = 'python-auspost',
        version = pep386(version),
        url = 'http://bitbucket.org/goodtune/python-auspost',
        author = 'Gary Reynolds',
        author_email = 'gary@touch.asn.au',
        description = open(README).read(),
        install_requires = ['anyjson', 'httplib2'],
        packages = ['auspost'],
    )
