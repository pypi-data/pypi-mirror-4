#!/usr/bin/env python
# coding:utf-8 vi:et:ts=2

# autowsgiserver information
# Copyright 2012 Grigory Petrov
# See LICENSE for details.

import os
import pkg_resources

NAME_SHORT = "autowsgiserver"
VER_MAJOR = 0
VER_MINOR = 1
VER_TXT = pkg_resources.require( NAME_SHORT )[ 0 ].version
DIR_THIS = os.path.dirname( os.path.abspath( __file__ ) )
NAME_FULL = "WSGI server that auto serves apps in target directory."
DESCR = """
CherryPy based WSGI server that scans specified dir for WSGI clients and run
them as WSGI applications with different virtual hosts. Allows to run
multiple simple web applications on one server without any configuration.

Version {s_ver_txt}
""".replace( '\n', '' ).strip().replace( '  ', ' ' ).format(
  s_ver_txt = VER_TXT )

