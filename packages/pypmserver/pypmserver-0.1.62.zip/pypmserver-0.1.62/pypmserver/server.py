#!/usr/bin/env python
# coding:utf-8 vi:et:ts=2

# pypmserver xmlrpc server code.
# Copyright 2013 Grigory Petrov
# See LICENSE for details.

import os
import threading
import time
import logging
import xmlrpclib

import cherrypy
import jinja2

import info
import context
import background_tasks
import task_cleaner
import index
from model_user import User


DIR_THIS = os.path.dirname( os.path.abspath( __file__ ) )
DIR_TEMPLATES = os.path.join( DIR_THIS, 'templates' )
ENV = jinja2.Environment( loader = jinja2.FileSystemLoader( DIR_TEMPLATES ) )


class Api( cherrypy._cptools.XMLRPCController ) :


  def __init__( self ) :
    cherrypy._cptools.XMLRPCController.__init__( self )
    self.__oLock = threading.Lock()
    self.__mTasks = {}
    self.__nIdNext = 10


  @cherrypy.expose
  ##x Called if API is accessed via web browser.
  def ERRORMETHOD( self, s_params ) :
    return True


  @cherrypy.expose
  def task_new( self ) :
    with self.__oLock :
      nId = self.__idNext()
      self.__mTasks[ nId ] = {
        'status' : 'new',
        'id' :     nId,
        'time' :   time.time(),
      }
    return nId


  @cherrypy.expose
  def task_del( self, n_id ) :
    with self.__oLock :
      if n_id in self.__mTasks :
        if self.__mTasks[ n_id ][ 'status' ] in [ 'new', 'done' ] :
          del self.__mTasks[ n_id ]
          return True
    return False


  @cherrypy.expose
  def task_field_set( self, n_id, s_field, u_val ) :
    assert isinstance( s_field, basestring )
    s_field = s_field.strip()
    with self.__oLock :
      if n_id in self.__mTasks :
        mTask = self.__mTasks[ n_id ]
        mTask[ 'time' ] = time.time()
        mTask[ s_field ] = u_val
        return True
    return False


  @cherrypy.expose
  def task_field_get( self, n_id, s_field ) :
    assert isinstance( s_field, basestring )
    s_field = s_field.strip()
    with self.__oLock :
      if n_id in self.__mTasks :
        mTask = self.__mTasks[ n_id ]
        mTask[ 'time' ] = time.time()
        return mTask[ s_field ]
    return False


  @cherrypy.expose
  def task_field_upload( self, n_id, s_field, o_data ) :
    assert isinstance( s_field, basestring )
    assert isinstance( o_data, xmlrpclib.Binary )
    s_field = s_field.strip()
    with self.__oLock :
      if n_id in self.__mTasks :
        mTask = self.__mTasks[ n_id ]
        mTask[ 'time' ] = time.time()
        if s_field in mTask :
          mTask[ s_field ] += o_data.data
        else :
          mTask[ s_field ] = o_data.data
        return True
    return False


  @cherrypy.expose
  def task_start( self, n_id ) :
    with self.__oLock :
      if n_id in self.__mTasks :
        self.__mTasks[ n_id ][ 'status' ] = 'queued'
        ##  After some time task status will be changed to 'inprogress'
        ##  and after completion it will be 'done'.
        background_tasks.instance.add( self.__mTasks[ n_id ] )
        return True
    return False


  @cherrypy.expose
  def package_info( self, s_name ) :
    return list( index.info(
      s_package = s_name,
      s_dirRoot = context.instance.dirWebserver() ) )


  ##x Called by TaskCleaner, since this object is the owner for tasks list.
  def tasksCleanup( self ) :
    SEC_BEFORE_DEL = 60
    dTimeCur = time.time()
    with self.__oLock :
      for nId, mTask in self.__mTasks.items() :
        if dTimeCur > mTask[ 'time' ] + SEC_BEFORE_DEL :
          del self.__mTasks[ nId ]


  def __idNext( self ) :
    nId = self.__nIdNext
    self.__nIdNext += 1
    return nId


def auth( s_realm, s_username ) :
  oUsers = User.select( User.q.s_name == s_username )
  if oUsers.count() :
    return oUsers.getOne().s_pass_a1
  return None


def serve_path( s_path ) :
  if '/' == s_path :
    if context.instance.isWriteLock() :
      return ENV.get_template( 'busy.html' ).render()
    else :
      return ENV.get_template( 'index.html' ).render()
  else :
    try :
      context.instance.readLock()
      sPath = context.instance.dirWebserver() + s_path.replace( '/', '\\' )
      return cherrypy.lib.static.serve_file( sPath )
    finally :
      context.instance.readUnlock()


def start( m_args ) :

  ##  Create dirs.
  context.instance.create()

  cherrypy.engine.autoreload.unsubscribe()
  cherrypy.config.update( {
    'server.socket_host' : '0.0.0.0',
  } )

  ##  Will process all tasks in one, background thread. App() will put
  ##  ready tasks into it's query.
  background_tasks.instance.subscribe()
  ##  Will clear tasks that was not updated by clients for long time
  ##  (normally client will delete task after it's completed, but client
  ##  can have network problems.
  task_cleaner.instance.subscribe()

  oDispatcher = cherrypy.dispatch.RoutesDispatcher()
  oDispatcher.connect( 'all', '{s_path:(.+)}', serve_path )
  oCfg = { '/' : { 'request.dispatch' : oDispatcher } }
  oApp = cherrypy.tree.mount( None, '/', oCfg )
  oApp.log.access_log.setLevel( logging.ERROR )
  oApp = cherrypy.tree.mount( Api(), '/api', config = { '/' : {
    'tools.auth_digest.on' :      True,
    'tools.auth_digest.realm' :   info.NAME_SHORT,
    'tools.auth_digest.get_ha1' : auth,
    'tools.auth_digest.key' :     'a45d67a5-a8e0-4c6a-ab5d-cb3c70b5aa99',
  } } )
  oApp.log.access_log.setLevel( logging.ERROR )
  for s in [ 'signal_handler', 'console_control_handler' ] :
    if hasattr( cherrypy.engine, s ) :
      getattr( cherrypy.engine, s ).subscribe()
  cherrypy.engine.start()
  cherrypy.engine.block()

