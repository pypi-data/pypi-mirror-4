#!/usr/bin/env python
# coding:utf-8 vi:et:ts=2

# autowsgiserver information
# Copyright 2012 Grigory Petrov
# See LICENSE for details.

import os
DIR_THIS = os.path.dirname( os.path.abspath( __file__ ) )
##! One dir up in path, where |setup.py| and |.hg| are placed.
DIR_ROOT = os.sep.join( DIR_THIS.split( os.sep )[ : -1 ] )

try :
  ##  If this file exist, package is installed from pypi.
  with open( 'PKG-INFO' ) as oFile :
    import rfc822
    import re
    sVer = rfc822.Message( oFile ).get( 'version' ).strip()
    oMatch = re.match( r'\d+\.\d+\.(\d+)', sVer )
    if oMatch :
      VER_BUILD = int( oMatch.group( 1 ) )
except :
  ##  Not installed from pypi, try to get version from VCS.
  try :
    import subprocess
    sId = subprocess.check_output( [ 'hg', '-R', DIR_ROOT, 'id', '-n' ] )
    VER_BUILD = int( sId.strip( '+\n' ) )
  except (subprocess.CalledProcessError, OSError) :
    ##* Temporary hack, need better install system.
    VER_BUILD = 0

NAME_SHORT = "autowsgiserver"
NAME_FULL = "WSGI server that auto serves apps in target directory."
DESCR = """
CherryPy based WSGI server that scans specified dir for WSGI clients and run
them as WSGI applications with different virtual hosts. Allows to run
multiple simple web applications on one server without any configuration.
""".replace( '\n', '' ).strip().replace( '  ', ' ' )
VER_MAJOR = 0
VER_MINOR = 1
VER_TXT = ".".join( map( str, [ VER_MAJOR, VER_MINOR, VER_BUILD ] ) )

