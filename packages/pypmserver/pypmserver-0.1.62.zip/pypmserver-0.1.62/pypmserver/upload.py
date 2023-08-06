#!/usr/bin/env python
# coding:utf-8 vi:et:ts=2

# pypmserver xmlrpc client code for uploading .pypm packages to server.
# Copyright 2013 Grigory Petrov
# See LICENSE for details.

import xmlrpclib
import os
import time

from support_xmlrpc import DigestTransport


def main( s_remote, s_user, s_pass, s_path ) :

  assert isinstance( s_remote, basestring )
  s_remote = s_remote.rstrip( '/' )
  if s_remote.startswith( 'http://' ) :
    s_remote = s_remote.replace( 'http://', '', 1 )
  sUrl = 'http://{s_user}:{s_pass}@{s_remote}/api'.format( ** locals() )
  oRemote = xmlrpclib.ServerProxy( sUrl, transport = DigestTransport() )
  BYTES_IN_UPLOAD_CHUNK = 1024 * 64
  with open( s_path, 'rb' ) as oFile :
    nId = oRemote.task_new()
    oRemote.task_field_set( nId, 'type', 'upload' )
    oRemote.task_field_set( nId, 'file_name', os.path.basename( s_path ) )
    while True :
      sData = oFile.read( BYTES_IN_UPLOAD_CHUNK )
      if not sData :
        break
      sData = xmlrpclib.Binary( sData )
      oRemote.task_field_upload( nId, 'file_data', sData )
    oRemote.task_start( nId )
  print( "Waiting for task to be processes...")
  while True :
    sStatus = oRemote.task_field_get( nId, 'status' )
    if 'done' == sStatus :
      break
    time.sleep( 0.5 )
  print( "Task processed." )
  oRemote.task_del( nId )

