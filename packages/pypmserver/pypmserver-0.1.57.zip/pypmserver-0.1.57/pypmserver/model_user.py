#!/usr/bin/env python
# coding:utf-8 vi:et:ts=2

# pypmserver database model for 'user' objects.
# Copyright 2013 Grigory Petrov
# See LICENSE for details.

import sqlobject

import info

DB_CONN = sqlobject.sqlite.builder()( info.DB_FILE_PATH )


class User( sqlobject.SQLObject ) :


  _connection = DB_CONN
  s_name = sqlobject.StringCol()
  ##  HTTP Digest auth 'A1' password hash.
  s_pass_a1 = sqlobject.StringCol()


User.createTable( ifNotExists = True )

