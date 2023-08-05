#!/usr/bin/env python
# coding:utf-8 vi:et:ts=2

# autowsgiserver applications management.
# Copyright 2013 Grigory Petrov
# See LICENSE for details.

import sys
import os


class Apps( object ) :
  """
  Loads python packages that are WSGI applications and lookups corresponding
  application WSGI handling function based on HTTP request host.
  """


  def __init__( self ) :
    self.__lApps = []
    ##  What application to user for what virtual host.
    self.__mAppForHost = {}


  def load( self, s_name ) :
    """
    Load python package that is WSGI application.
    """
    try :
      ##! Prevent loading modules second time. For example, if autowsgiserver
      ##  is started inside a folder where it's placed, this can lead to
      ##  problems.
      if s_name not in sys.modules :
        oApp = __import__( s_name )
        if hasattr( oApp, 'application' ) :
          self.__lApps.append( oApp )
        else :
          del sys.modules[ s_name ]
    except ImportError :
      pass


  def count( self ) :
    return len( self.__lApps )


  def handler( self, s_host = None ) :
    """
    Given HTTP request hostname searches for application that want to handle
    it and evaluates to this app's WSGI handler callable.
    """
    oApp = self.__mAppForHost.get( s_host )
    ##  Application for this virtual host not yet selected?
    if not oApp :
      ##  Serve single app if hostname is not defined and app don't want
      ##  specific hostname.
      if s_host is None :
        assert 1 == self.count()
        oApp = self.__lApps[ 0 ]
        if not hasattr( oApp, 'virtualhost' ) :
          self.__mAppForHost[ s_host ] = oApp
      else :
        ##  First try to find application that explicitly wants host.
        sHostRequired, _, _ = s_host.partition( ':' )
        for oApp in self.__lApps :
          if hasattr( oApp, 'virtualhost' ) :
            uVirtualhost = oApp.virtualhost()
            if not hasattr( uVirtualhost, '__iter__' ) :
              lVirtualhosts = [ uVirtualhost ]
            else :
              lVirtualhosts = uVirtualhost
            for sVirtualhost in lVirtualhosts :
              sHostForApp, _, _ = sVirtualhost.partition( ':' )
              if sHostForApp.strip() in sHostRequired :
                self.__mAppForHost[ s_host ] = oApp
                break
            else :
              ##  Not found
              continue
            ##  Found
            break
        ##  If no app wants this hostname, try app dir names.
        else :
          for oApp in self.__lApps :
            sAppDir = os.path.dirname( oApp.__file__ ).split( os.sep )[ -1 ]
            if sAppDir in sHostRequired :
              self.__mAppForHost[ s_host ] = oApp
              break
          ##  If no app dir match serve single app that don't want hostname
          else :
            if 1 == self.count() :
              oApp = self.__lApps[ 0 ]
              if not hasattr( oApp, 'virtualhost' ) :
                self.__mAppForHost[ s_host ] = oApp
      oApp = self.__mAppForHost.get( s_host )
    return oApp.application if oApp else None


instance = Apps()

