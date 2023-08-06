#!/usr/bin/env python
# coding:utf-8 vi:et:ts=2

# autowsgiserver applications management.
# Copyright 2013 Grigory Petrov
# See LICENSE for details.

import sys
import os

import context


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


  def appMatchHostname( self, o_app, s_host ) :
    if hasattr( o_app, 'virtualhost' ) :
      uNames = o_app.virtualhost()
      if not hasattr( uNames, '__iter__' ) :
        lNames = [ uNames ]
      else :
        lNames = uNames
      sGivenName, _, _ = s_host.partition( ':' )
      for sName in lNames :
        sExpectedName, _, _ = sName.partition( ':' )
        if sGivenName in sExpectedName or sExpectedName in sGivenName :
          return True


  def appdirMatchHostname( self, o_app, s_host ) :
    sAppDir = os.path.dirname( o_app.__file__ ).split( os.sep )[ -1 ]
    sGivenName, _, _ = s_host.partition( ':' )
    if sGivenName in sAppDir or sAppDir in sGivenName :
      return True


  def appServeEmptyHost( self, o_app ) :
    if not hasattr( oApp, 'virtualhost' ) :
      return True
    if context.instance.force :
      if self.appMatchHostname( o_app, context.instance.force ) :
        return True


  def handler( self, s_host = None ) :
    """
    Given HTTP request hostname searches for application that want to handle
    it and evaluates to this app's WSGI handler callable.
    """
    oApp = self.__mAppForHost.get( s_host )
    sForce = context.instance.force
    ##  Application for this virtual host not yet selected?
    if not oApp :
      ##  Serve single app if hostname is not defined and app don't want
      ##  specific hostname or 'force server' option is set for localhost
      ##  debug.
      if s_host is None :
        for oApp in self.__lApps :
          if self.appServeEmptyHost( oApp ) :
            self.__mAppForHost[ s_host ] = oApp
            break
      else :
        ##  First try to find application that explicitly wants host.
        for oApp in self.__lApps :
          if self.appMatchHostname( oApp, sForce or s_host ) :
            self.__mAppForHost[ s_host ] = oApp
            break
        ##  If no app wants this hostname, try app dir names.
        else :
          for oApp in self.__lApps :
            if self.appdirMatchHostname( oApp, sForce or s_host ) :
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

