#!/usr/bin/env python
# coding:utf-8 vi:et:ts=2

# pypmserver background thread that periodically kills abandoned tasks.
# Copyright 2013 Grigory Petrov
# See LICENSE for details.

import threading
import time

import cherrypy


##x Background thread that will periodically delete tasks that was
##  not deleted by clients.
class TaskCleaner( cherrypy.process.plugins.SimplePlugin ) :


  def __init__( self, o_bus ) :
    cherrypy.process.plugins.SimplePlugin.__init__( self, o_bus )
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
      time.sleep( 0.2 )
      cherrypy.tree.apps[ '/api' ].root.tasksCleanup()


instance = TaskCleaner( cherrypy.engine )

