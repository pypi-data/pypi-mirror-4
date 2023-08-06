#!/usr/bin/env python
# coding:utf-8 vi:et:ts=2

# pypmserver global context definition.
# Copyright 2013 Grigory Petrov
# See LICENSE for details.

import os
import threading
import time

import info


class Context( object ) :


  def __init__( self ) :
    sDir = '.{0}'.format( info.NAME_SHORT )
    self.__sDirRoot = os.path.join( os.path.expanduser( '~' ), sDir )
    self.__sDirCache = os.path.join( self.__sDirRoot, 'cache' )
    self.__sDirWebserver = os.path.join( self.__sDirRoot, 'webserver' )
    self.__oLock = threading.Lock()
    self.__nReaders = 0
    self.__nWriters = 0


  def create( self ) :
    if not os.path.isdir( self.__sDirRoot ) :
      os.makedirs( self.__sDirRoot )
    if not os.path.isdir( self.__sDirCache ) :
      os.makedirs( self.__sDirCache )
    if not os.path.isdir( self.__sDirWebserver ) :
      os.makedirs( self.__sDirWebserver )


  def dirRoot( self ) :
    return self.__sDirRoot


  def dirCache( self ) :
    return self.__sDirCache


  def dirWebserver( self ) :
    return self.__sDirWebserver


  ##x Read-write lock. Pypm reads repository, 'upload' command updates it.
  def readLock( self ) :
    while True :
      if self.__nWriters > 0 :
        time.sleep( 0.1 )
      else :
        with self.__oLock :
          if 0 == self.__nWriters :
            self.__nReaders += 1
            return


  ##x Read-write lock. Pypm reads repository, 'upload' command updates it.
  def readUnlock( self ) :
    with self.__oLock :
      assert self.__nReaders > 0
      self.__nReaders -= 1


  ##x Read-write lock. Pypm reads repository, 'upload' command updates it.
  def writeLock( self ) :
    ##  No new readers after this.
    self.__nWriters += 1
    while True :
      if self.__nReaders > 0 :
        time.sleep( 0.1 )
      self.__oLock.acquire()
      assert 0 == self.__nReaders
      assert 1 == self.__nWriters
      return


  ##x Read-write lock. Pypm reads repository, 'upload' command updates it.
  def writeUnlock( self ) :
    assert 0 == self.__nReaders
    assert 1 == self.__nWriters
    self.__nWriters -= 1
    self.__oLock.release()


  ##x Read-write lock. Pypm reads repository, 'upload' command updates it.
  def isWriteLock( self ) :
    return self.__nWriters > 0


instance = Context()

