#!/usr/bin/env python
# coding:utf-8 vi:et:ts=2

from setuptools import setup
from autowsgiserver.info import NAME_SHORT, DESCR, VER_TXT

setup(
  name         = NAME_SHORT,
  version      = VER_TXT,
  description  = DESCR,
  author       = "Grigory Petrov",
  author_email = "grigory.v.p@gmail.com",
  url          = "http://bitbucket.org/eyeofhell/{0}".format( NAME_SHORT ),
  license      = 'GPLv3',
  packages     = [ NAME_SHORT ],
  zip_safe     = True,
  install_requires = [
    ##  Simple WSGI server engine.
    'cherrypy',
  ],
  entry_points = {
    'console_scripts' : [
      '{0} = {0}:main'.format( NAME_SHORT ),
    ],
  },
  ##  http://pypi.python.org/pypi?:action=list_classifiers
  classifiers  = [
    'Development Status :: 1 - Planning',
    'Environment :: Console',
    'Intended Audience :: System Administrators',
    'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
    'Natural Language :: English',
    'Operating System :: OS Independent',
    'Programming Language :: Python :: 2.7',
    'Topic :: Internet :: WWW/HTTP :: HTTP Servers',
  ]
)

