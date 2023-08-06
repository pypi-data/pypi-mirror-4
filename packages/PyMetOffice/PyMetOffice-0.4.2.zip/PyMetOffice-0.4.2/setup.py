#!/usr/bin/python
from distutils.core import setup

CLASSIFIERS = ['Development Status :: 4 - Beta',
               'Intended Audience :: Developers',
               'License :: OSI Approved :: MIT License',
               'Operating System :: OS Independent',
               'Programming Language :: Python :: 2',
               'Topic :: Software Development :: Libraries :: Python Modules'
               ]

INFO = {
   'name': 'PyMetOffice',
   'version': '0.4.2',
   'packages': ['pymetoffice'],
   'description': 'Python interface to UK Met Office DataPoint API',
   'url': 'http://pypi.python.org/PyMetOffice',
   'author': 'Bob Margolis',
   'author_email': 'netherwyndham@gmail.com',
   'package_dir': {'pymetoffice': 'pymetoffice'}
}

setup(classifiers=CLASSIFIERS, **INFO)
