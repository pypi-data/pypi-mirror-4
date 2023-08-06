#!/usr/bin/env python
# coding:utf-8 vi:et:ts=2

# pypmserver entry point.
# Copyright 2013 Grigory Petrov
# See LICENSE for details.

import argparse
import hashlib

from pyedsl import pd

import info


def cmdUserList( m_args ) :
  from model_user import User
  for oUser in User.select() :
    print( oUser.s_name )


def cmdUserAdd( m_args ) :
  from model_user import User
  sUser = m_args[ 'user' ]
  sPass = m_args[ 'pass' ]
  if User.select( User.q.s_name == sUser ).count() :
    print( "User '{0}' already exist.".format( sUser ) )
    return
  sPlaintext = '{0}:{1}:{2}'.format( sUser, info.AUTH_REALM, sPass )
  sHash = hashlib.md5( sPlaintext ).hexdigest()
  User( s_name = sUser, s_pass_a1 = sHash )


def cmdUserDel( m_args ) :
  from model_user import User
  sUser = m_args[ 'user' ]
  oUsers = User.select( User.q.s_name == sUser )
  if not oUsers.count() :
    print( "User '{0}' unknown.".format( sUser ) )
    return
  if oUsers.count() > 1 :
    print( "Internal consistency error." )
    return
  User.delete( oUsers.getOne().id )


def cmdUserChangePass( m_args ) :
  from model_user import User
  sUser = m_args[ 'user' ]
  sPass = m_args[ 'newpass' ]
  oUsers = User.select( User.q.s_name == sUser )
  if not oUsers.count() :
    print( "User '{0}' unknown.".format( sUser ) )
    return
  if oUsers.count() > 1 :
    print( "Internal consistency error." )
    return
  sPlaintext = '{0}:{1}:{2}'.format( sUser, info.AUTH_REALM, sPass )
  oUsers.getOne().s_pass_a1 = hashlib.md5( sPlaintext ).hexdigest()


def cmdStart( m_args ) :
  print( "Starting..." )
  import server
  server.start( m_args )


def cmdUpload( m_args ) :
  print( "Uploading..." )
  import upload
  upload.main(
    s_remote = m_args[ 'remote' ],
    s_user = m_args[ 'user' ],
    s_pass = m_args[ 'pass' ],
    s_path = m_args[ 'path' ], )


def cmdPackageInfo( m_args ) :

  print( "Requesting package information ..." )
  import xmlrpclib
  from support_xmlrpc import DigestTransport

  sRemote = m_args[ 'remote' ].rstrip( '/' )
  if sRemote.startswith( 'http://' ) :
    sRemote = sRemote.replace( 'http://', '', 1 )
  sUrl = 'http://{s_user}:{s_pass}@{s_remote}/api'.format(
    s_user = m_args[ 'user' ],
    s_pass = m_args[ 'pass' ],
    s_remote = sRemote )
  oRemote = xmlrpclib.ServerProxy( sUrl, transport = DigestTransport() )
  sPackage = m_args[ 'name' ]
  lPackages = oRemote.package_info( sPackage )
  if not lPackages :
    print( "Package '{0}' not in index".format( sPackage ) )
    exit( 1 )
  for mPackage in lPackages :
    sTitle = "{name} {osarch} {pyver}".format( ** mPackage )
    print( sTitle )
    ##  Check that depends are available.
    for sDepenency in mPackage[ 'install_requires' ][ "" ] :
      if not oRemote.package_info( sDepenency ) :
        print( "  Dependency '{0}' not found".format( sDepenency ) )


def main() :
  with pd.wrap( argparse.ArgumentParser() ) as oParser :
    with pd.wrap( pd.o.add_subparsers() ) :
      with pd.wrap( pd.o.add_parser( 'start' ) ) :
        pd.o.set_defaults( handler = cmdStart )
      with pd.wrap( pd.o.add_parser( 'upload' ) ) :
        pd.o.add_argument( '--remote', required = True )
        pd.o.add_argument( '--user', required = True )
        pd.o.add_argument( '--pass', required = True )
        pd.o.add_argument( 'path' )
        pd.o.set_defaults( handler = cmdUpload )
      with pd.wrap( pd.o.add_parser( 'package' ) ) :
        with pd.wrap( pd.o.add_subparsers() ) :
          with pd.wrap( pd.o.add_parser( 'info' ) ) :
            pd.o.set_defaults( handler = cmdPackageInfo )
            pd.o.add_argument( '--remote', required = True )
            pd.o.add_argument( '--user', required = True )
            pd.o.add_argument( '--pass', required = True )
            pd.o.add_argument( 'name', nargs = '?', default = '*' )
      with pd.wrap( pd.o.add_parser( 'user' ) ) :
        with pd.wrap( pd.o.add_subparsers() ) :
          with pd.wrap( pd.o.add_parser( 'list' ) ) :
            pd.o.set_defaults( handler = cmdUserList )
          with pd.wrap( pd.o.add_parser( 'add' ) ) :
            pd.o.add_argument( '--user', required = True )
            pd.o.add_argument( '--pass', required = True )
            pd.o.set_defaults( handler = cmdUserAdd )
          with pd.wrap( pd.o.add_parser( 'del' ) ) :
            pd.o.add_argument( '--user', required = True )
            pd.o.set_defaults( handler = cmdUserDel )
          with pd.wrap( pd.o.add_parser( 'changepass' ) ) :
            pd.o.add_argument( '--user', required = True )
            pd.o.add_argument( '--newpass', required = True )
            pd.o.set_defaults( handler = cmdUserChangePass )
  oArgs = oParser.parse_args()
  oArgs.handler( vars( oArgs ) )

