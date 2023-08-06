#!/usr/bin/env python
# coding:utf-8 vi:et:ts=2

# autowsgiserver global context.
# Copyright 2013 Grigory Petrov
# See LICENSE for details.


class Context( object ) :


  def __init__( self ) :
    ##  Part of WSGI app name to force enable (for localhost debugging
    ##  if app wants specific virtual host name).
    self.force = None


  def setCmdArgs( self, m_args ) :
    if 'force' in m_args :
      self.force = m_args[ 'force' ]


instance = Context()

