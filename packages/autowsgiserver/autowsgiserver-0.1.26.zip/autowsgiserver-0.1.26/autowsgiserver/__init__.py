#!/usr/bin/env python
# coding:utf-8 vi:et:ts=2

# autowsgiserver core
# Copyright 2013 Grigory Petrov
# See LICENSE for details.

import os
import sys
import argparse
import re

import cherrypy.wsgiserver

import info
import apps
import context


def loadApps( s_dir ) :
  """
  Import python packages from specified dir as WSGI apps.
  """
  if not os.path.isdir( s_dir ) :
    print( "Error: '{0}' is not a directory.".format( s_dir ) )
    exit( 1 )
  lDirs = []
  for sItem in os.listdir( s_dir ) :
    if os.path.isdir( os.path.join( s_dir, sItem ) ) :
      ##  Package dir name must be valid python identifier.
      if re.match( r'^[a-zA-Z_]\w*$', sItem ) :
        lDirs.append( sItem )
  if not lDirs :
    print( "Error: '{0}' don't have any python packages.".format( s_dir ) )
    exit( 1 )
  sys.path.append( s_dir )
  for sDir in lDirs :
    apps.instance.load( sDir )
  if apps.instance.count() :
    print( "{0} aplications loaded".format( apps.instance.count() ) )
  else :
    print( "Error: '{0}' don't have any python WSGI apps.".format( s_dir ) )
    exit( 1 )


def wsgiHandler( m_context, x_response ) :
  """
  Middleware that translates Cherrypy WSGI server calls into WSGI calls
  for corresponding app selected based on virtualhost.
  """
  if 'HTTP_HOST' not in m_context :
    xHandler = apps.instance.handler()
  else :
    xHandler = apps.instance.handler( m_context[ 'HTTP_HOST' ] )
  if xHandler :
    return  xHandler( m_context, x_response )
  x_response( '404 NOT FOUND', [ ( 'Content-Type', 'text/plain' ) ] )
  return [ 'Not found' ]


def main() :
  oParser = argparse.ArgumentParser( description = info.DESCR )
  oParser.add_argument( 'path', help = "Directory to search for WSGI apps." )
  oParser.add_argument( '--force', help = "Enable app with specified name" )
  oArgs = oParser.parse_args()
  context.instance.setCmdArgs( vars( oArgs ) )
  loadApps( os.path.abspath( oArgs.path ) )
  gAddr = ( '0.0.0.0', 8080 )
  oServer = cherrypy.wsgiserver.CherryPyWSGIServer( gAddr, wsgiHandler )
  try :
    oServer.start()
  except KeyboardInterrupt :
    oServer.stop()

