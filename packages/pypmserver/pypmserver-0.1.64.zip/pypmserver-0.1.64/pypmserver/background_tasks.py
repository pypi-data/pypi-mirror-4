#!/usr/bin/env python
# coding:utf-8 vi:et:ts=2

# pypmserver background process.
# Copyright 2013 Grigory Petrov
# See LICENSE for details.

import os
import Queue
import threading
import time

import cherrypy
import index

import context


class BackgroundTasks( cherrypy.process.plugins.SimplePlugin ) :


  def __init__( self, o_bus ) :
    cherrypy.process.plugins.SimplePlugin.__init__( self, o_bus )
    self.__oTasks = Queue.Queue()
    self.__oThread = None
    self.__fRunning = False


  def start( self ) :
    if not self.__oThread :
      self.__oThread = threading.Thread( target = self.run )
      self.__fRunning = True
      self.__oThread.start()
  ##  After daemonizer.
  start.priority = 80


  def stop( self ) :
    if self.__fRunning :
      ##  This will stop thread after some time.
      self.__fRunning = False
      self.__oThread.join()
      ##  For next |start()| to work correctly.
      self.__oThread = None


  def run( self ) :
    while self.__fRunning :
      try :
        mTask = self.__oTasks.get( block = True, timeout = 0.2 )
      ##  Timeout?
      except Queue.Empty :
        ##  Check |self.__fRunning|.
        continue
      self.__taskHandle( mTask )


  def add( self, m_task ) :
    self.__oTasks.put_nowait( m_task )

  def __taskHandle( self, m_task ) :
    m_task[ 'status' ] = 'inprogress'
    try :
      if 'type' in m_task :
        if 'upload' == m_task[ 'type' ] :
          self.__taskHandleUpload( m_task )
    finally :
      ##  Mark that task can be deleted after it's result is read by
      ##  client. If client can't delete task (disconnect etc) task will
      ##  be deleted after some time via |TaskCleaner| plugin. To detect
      ##  such tasks 'time' field is used.
      m_task[ 'status' ] = 'done'
      m_task[ 'time' ] = time.time()


  def __taskHandleUpload( self, m_task ) :
    try :
      context.instance.writeLock()
      index.addPypm(
        s_fileName = m_task[ 'file_name' ],
        s_fileData = m_task[ 'file_data' ],
        s_dirRoot = context.instance.dirWebserver() )
    finally :
      context.instance.writeUnlock()


instance = BackgroundTasks( cherrypy.engine )

