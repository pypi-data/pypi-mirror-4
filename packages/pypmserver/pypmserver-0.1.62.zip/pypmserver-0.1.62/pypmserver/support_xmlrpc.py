#!/usr/bin/env python
# coding:utf-8 vi:et:ts=2

# pypmserver code for python xmlrpc to support DIGEST auth.
# Copyright 2013 Grigory Petrov
# See LICENSE for details.

import urllib
import string
import random
import base64
import httplib
import xmlrpclib
import hashlib


##c Can be used as xmlrpclib.ServerProxy transport to enable HTTP DIGEST
##  authentication via HTTP (no HTTPS yet).
class DigestTransport( xmlrpclib.Transport ) :


  def __discardCurrentResponse( self, o_resp ) :
    ##  Discard current response so new request can proceed.
    if o_resp.getheader( 'content-length', 0 ) :
      o_resp.read()


  def __writeAuthBasic( self, s_host ) :
    sCred, _ = urllib.splituser( s_host )
    sAuth = base64.b64encode( urllib.unquote( sCred ) )
    sValue = 'Basic {0}'.format( sAuth )
    self._extra_headers.append( ( 'Authorization', sValue ) )


  def __writeAuthDigest( self, s_host, s_params, s_body, s_handler,
    n_nonce ) :

    ##  |s_params| is like
    ##  |realm="a", nonce="1a:2b", algorithm="MD5", qop="auth"|
    mParams = {}
    for sPair in [ s.strip() for s in s_params.split( ',' ) ] :
      sKey, _, sVal = sPair.partition( '=' )
      mParams[ sKey.strip() ] = sVal.strip().strip( '"' )
    sCred, _ = urllib.splituser( s_host )
    sCred = urllib.unquote( sCred )
    USER, _, PASS = [ s.strip() for s in sCred.partition( ':' ) ]
    assert USER and PASS
    assert 'MD5' == mParams[ 'algorithm' ].upper()

    ##  Generate HTTP DIGEST AUTH response.
    def digest( * vargs ) :
      return hashlib.md5( ':'.join( vargs ) ).hexdigest()
    REALM = mParams[ 'realm' ]
    NONCE = mParams[ 'nonce' ]
    BODY = hashlib.md5( s_body ).hexdigest()
    QOP = mParams[ 'qop' ] if 'qop' in mParams else None
    HA1 = digest( USER, REALM , PASS )
    NC = None
    CNONCE = None
    if 'auth' == QOP :
      HA2 = digest( 'POST', s_handler )
    else :
      HA2 = digest( 'POST', s_handler, BODY )
    if not QOP :
      RESPONSE = digest( HA1, NONCE, HA2 )
    else :
      NC = '{:08d}'.format( n_nonce )
      sChars = string.ascii_letters + string.digits
      lChars = [ random.choice( sChars ) for i in range( 16 ) ]
      CNONCE = ''.join( lChars )
      RESPONSE = digest( HA1, NONCE, NC, CNONCE, QOP, HA2 )

    lResponse = [
      'username="{0}"'.format( USER ),
      'realm="{0}"'.format( REALM ),
      'nonce="{0}"'.format( NONCE ),
      'uri="{0}"'.format( s_handler ),
      'algorithm="MD5"',
      'response="{0}"'.format( RESPONSE ),
    ]
    if QOP is not None :
      lResponse.append( 'qop="{0}"'.format( QOP ) )
    if NC is not None :
      lResponse.append( 'nc="{0}"'.format( NC ) )
    if CNONCE is not None :
      lResponse.append( 'cnonce="{0}"'.format( CNONCE ) )
    sValue = 'Digest {0}'.format( ', '.join( lResponse ) )
    self._extra_headers.append( ( 'Authorization', sValue ) )


  ##x Called by original implementation to send prepared XMLRPC request
  ##  to server, receive response and parse it. Can be called up to 2
  ##  times to overcome zombie keep-alive connections.
  def single_request( self,
    ##i URL passed to |xmlrpclib.ServerProxy|.
    host,
    ##i URI from HTTP header, ex "/api".
    handler,
    ##i Formed XMLRPC request string that needs to be placed in HTTP body.
    request_body,
    ##i If logically True, verbose output need to be used.
    verbose = 0 ) :

    ##  Can't reuse existing connection?
    if not self._connection or host != self._connection[ 0 ]:
      sAuth, sHost = urllib.splituser( host )
      self._connection = host, httplib.HTTPConnection( sHost )
    oConn = self._connection[ 1 ]

    if hasattr( oConn, 'auth_digest_nonce_count' ) :
      oConn.auth_digest_nonce_count += 1
    else :
      oConn.auth_digest_nonce_count = 1

    try:
      self.send_request( oConn, handler, request_body )
      self.send_host( oConn, host )
      self.send_user_agent( oConn )
      self.send_content( oConn, request_body )

      oResp = oConn.getresponse( buffering = True )
      ##  Success?
      if 200 == oResp.status :
        self.verbose = verbose
        return self.parse_response( oResp )
      ##  Authorization required?
      if 401 == oResp.status :
        sChallenge = oResp.getheader( 'www-authenticate', '' )
        sMethod, _, sParams = sChallenge.partition( ' ' )
        ##  For next request to work.
        self.__discardCurrentResponse( oResp )

        if 'Basic' == sMethod :
          self.__writeAuthBasic( host )
          return self.single_request( host, handler, request_body, verbose )

        if 'Digest' == sMethod :
          self.__writeAuthDigest( host, sParams, request_body, handler,
            oConn.auth_digest_nonce_count )
          return self.single_request( host, handler, request_body, verbose )

    ##  Expected error?
    except xmlrpclib.Fault:
        raise
    ##  Unexpected error?
    except Exception:
      ##  Kill connection on unexpected error, can be in strange state.
      self.close()
      raise

    ##  Unknown response code. Discard response and raise.
    self.__discardCurrentResponse( oResp )
    raise xmlrpclib.ProtocolError( host + handler,
      oResp.status, oResp.reason, oResp.msg )

