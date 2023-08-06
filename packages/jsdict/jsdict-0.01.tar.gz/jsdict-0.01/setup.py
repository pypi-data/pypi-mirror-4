from distutils.core import setup
import sys

import jsdict

kw = dict(
    name = 'jsdict',
    version = "0.01",
    description = 'like Javascript dict',
    long_description = open('README', 'r').read(),
    author = 'zuroc',
    author_email = 'zsp007@gmail.com',
    py_modules = ['jsdict'],
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
