#!/usr/bin/env python
# coding:utf-8 vi:et:ts=2

# pypmserver pypm repository index code.
# Copyright 2013 Grigory Petrov
# See LICENSE for details.

import argparse
import os
import tarfile
import json
import shutil
import sqlite3
import gzip
import pickle
import StringIO


ABOUT_APP = "PYPM packages to PYPM repository converter."
##! tags VARCHAR can't be NULL due to pypm:package.py:300
CMD_CREATE = """
  CREATE TABLE IF NOT EXISTS "RepoPackage" (
    name VARCHAR NOT NULL,
    version VARCHAR NOT NULL,
    summary TEXT,
    description TEXT,
    keywords VARCHAR,
    home_page VARCHAR,
    license VARCHAR,
    author VARCHAR,
    author_email VARCHAR,
    maintainer VARCHAR,
    maintainer_email VARCHAR,
    install_requires BLOB,
    osarch VARCHAR NOT NULL,
    pyver VARCHAR NOT NULL,
    pkg_version VARCHAR NOT NULL,
    relpath VARCHAR,
    tags VARCHAR,
    PRIMARY KEY (name, version, osarch, pyver, pkg_version)
  );
"""

CMD_ADD = """
  INSERT INTO "RepoPackage" VALUES(
    :name,
    :version,
    :summary,
    :description,
    :keywords,
    :home_page,
    :license,
    :author,
    :author_email,
    :maintainer,
    :maintainer_email,
    :install_requires,
    :osarch,
    :pyver,
    :pkg_version,
    :relpath,
    :tags
  );
"""

CMD_QUERY_ALL = """
  SELECT * FROM "RepoPackage"
"""

CMD_QUERY_EXACT = """
  SELECT * FROM "RepoPackage" WHERE
    name = :s_name
    AND version = :s_version
    AND osarch = :s_osarch
    AND pyver = :s_pyver;
"""

CMD_QUERY_BY_NAME = """
  SELECT * FROM "RepoPackage" WHERE name LIKE :s_name
"""


def addPypm(
  ##i Name of .pypm file to add to index.
  s_fileName,
  ##i File content.
  s_fileData,
  ##i Index databases and files paths will be created from this root
  ##  path by adding to it python version dir (ex '2.7') and architecture
  ##  dir (ex 'win32-x86').
  s_dirRoot
) :

  assert s_fileName.endswith( '.pypm' )

  ##  Read meta information from package.
  oData = StringIO.StringIO( s_fileData )
  with tarfile.TarFile.gzopen( name = '', fileobj = oData ) as oPkg :
    mMeta = json.loads( oPkg.extractfile( 'info.json' ).read() )
  sDirIndex = os.path.join( s_dirRoot, mMeta[ 'pyver' ], mMeta[ 'osarch' ] )

  ##  Create path for database and packes if it's not exist.
  try :
    os.makedirs( sDirIndex )
  except OSError :
    ##  Already exist?
    pass
  assert os.path.isdir( sDirIndex )

  ##  Create index database or connect existing.
  sDb = os.path.join( sDirIndex, 'index' )
  with sqlite3.connect( sDb ) as oDb :

    ##  Allows to queue fetch result via column names.
    oDb.row_factory = sqlite3.Row

    ##  Create table if not exeist.
    oDb.execute( CMD_CREATE )

    ##  Check if item is already in database.
    oCursor = oDb.execute( CMD_QUERY_EXACT, {
      's_name' : mMeta[ 'name' ],
      's_version' : mMeta[ 'version' ],
      's_osarch' : mMeta[ 'osarch' ],
      's_pyver' : mMeta[ 'pyver' ],
    } )
    ##  Already in database?
    mItem = oCursor.fetchone()
    if mItem :
      ##  File already exists?
      if os.path.isfile( os.path.join( sDirIndex, mItem[ 'relpath' ] ) ) :
        ##  Package already added to index, do nothing.
        return
      else :
        ##* Integrity error.
        return

    ##  Create package file in index directory so it can be downloaded by
    ##  clients via web server.
    with open( os.path.join( sDirIndex, s_fileName ), 'wb' ) as oFile :
      oFile.write( s_fileData )

    ##  Register package in database.
    ##! PYPM uses protocol version 2.
    sRequires = pickle.dumps( mMeta[ 'install_requires' ], protocol = 2 )
    mCfg = {
      'name'              : mMeta[ 'name' ],
      'version'           : mMeta[ 'version' ],
      'summary'           : None,
      'description'       : None,
      'keywords'          : None,
      'home_page'         : None,
      'license'           : None,
      'author'            : None,
      'author_email'      : None,
      'maintainer'        : None,
      'maintainer_email'  : None,
      ##  { "" : [ "pip", "virtualenv", "mercurial" ] }
      'install_requires'  : buffer( sRequires ),
      'osarch'            : mMeta[ 'osarch' ],
      'pyver'             : mMeta[ 'pyver' ],
      'pkg_version'       : mMeta[ 'pkg_version' ],
      ##  Path is relative to the path 'index.gz' is downloaded from.
      'relpath'           : s_fileName,
      ##  String with text tags separated by spaces.
      ##  'be' for business edition.
      ##! Must be valid string.
      'tags'              : "",
    }
    oDb.execute( CMD_ADD, mCfg )

  ## After package added to databases, pack databases.
  sIndex = os.path.join( sDirIndex, 'index.gz' )
  with gzip.GzipFile( sIndex, 'w' ) as oIndex :
    oIndex.write( open( sDb, 'rb' ).read() )


def info( s_package, s_dirRoot ) :
  s_package = s_package.strip()
  for sDir in os.listdir( s_dirRoot ) :
    sDirPyver = os.path.join( s_dirRoot, sDir )
    if not os.path.isdir( sDirPyver ) :
      continue
    for sDir in os.listdir( sDirPyver ) :
      sDirOsarch = os.path.join( sDirPyver, sDir )
      if not os.path.isdir( sDirOsarch ) :
        continue
      sDb = os.path.join( sDirOsarch, 'index' )
      with sqlite3.connect( sDb ) as oDb :
        oDb.row_factory = sqlite3.Row
        ##  Info about all packages?
        if '*' == s_package :
          sQuery = CMD_QUERY_ALL
        else :
          sQuery = CMD_QUERY_BY_NAME
        mArgs = { 's_name' : '%{0}%'.format( s_package ) }
        for mItem in oDb.execute( sQuery, mArgs ).fetchall() :
          yield {
            'name' : mItem[ 'name' ],
            'pyver' : mItem[ 'pyver' ],
            'osarch' : mItem[ 'osarch' ],
            'install_requires' : pickle.loads( mItem[ 'install_requires' ] ),
          }

