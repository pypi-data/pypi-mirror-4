from distutils.core import setup
import sys

import tld_name

kw = dict(
    name = 'tld_name',
    version = "0.01",
    description = 'Top-level domain ( http://en.wikipedia.org/wiki/Top-level_domain )',
    long_description = open('README', 'r').read(),
    author = 'Michael Liao',
    author_email = 'askxuefeng@gmail.com',
    py_modules = ['tld_name'],
    classifiers = [
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ])

if sys.version_info[1]==5:
    kw['install_requires'] = ['simplejson']

setup(**kw)
