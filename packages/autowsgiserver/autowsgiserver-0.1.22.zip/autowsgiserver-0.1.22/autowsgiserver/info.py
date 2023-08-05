#!/usr/bin/env python
# coding:utf-8 vi:et:ts=2

# autowsgiserver information
# Copyright 2013 Grigory Petrov
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
{s_name_short} v. {s_ver_txt}\\n\\n
CherryPy based WSGI server that scans specified dir for WSGI clients and run
them as WSGI applications with different virtual hosts. Allows to run
multiple simple web applications on one server without any configuration.
""".replace( '\n', '' ).replace( '\\n', '\n' ).strip().format(
  s_name_short = NAME_SHORT,
  s_ver_txt = VER_TXT )

