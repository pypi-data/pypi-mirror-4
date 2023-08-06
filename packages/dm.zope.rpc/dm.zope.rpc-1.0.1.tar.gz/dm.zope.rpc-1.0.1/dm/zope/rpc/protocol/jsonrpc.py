# Copyright (C) 2010 by Dr. Dieter Maurer <dieter@handshake.de>; see 'LICENSE.txt' for details
"""An rpc protocol based on ``json``.

This requires Python 2.6's ``json`` module.
With minor modifications, this module can also be used with earlier
Python versions (tested with Python 2.4).

It implements http://json-rpc.org/wiki/specification
with some details from
http://groups.google.com/group/json-rpc/web/json-rpc-over-http.
However it lacks support for multiple rpc requests in a single
HTTP request and server to client rpc.

Note: The implementation requires a correct "Content-Type" for POST
requests. The specification recommends ``application/jsonrpc`` but
allows some other values. ``application/x-www-form-urlencoded`` is possible
provided that the body is indeed encoded in such a way and *params*
is base64 encoded (as required for GET requests).
Note: http://json-rpc.org/browser/trunk/python-jsonrpc/jsonrpc/proxy.py
gets it wrong. See ``jsonrpcproxy.py`` in this folder for a fixed version.
"""
from datetime import date, datetime
from json import dumps, loads

from dm.zope.rpc.interfaces import \
     IProtocolHandler, IMarshaller, IDataAdapter, \
     IErrorCode, IErrorMessage
from dm.zope.rpc.adapter import StandardDataAdapter
from dm.zope.rpc.marshaller import CommunicatingMarshallerBase
from dm.zope.rpc.handler import handlerfactory_from_marshaller
from dm.zope.rpc.type import binary
from dm.zope.rpc.util import is_standard_request



class JsonMarshaller(CommunicatingMarshallerBase):
  """Generic ``json-rpc`` marshaller."""

  content_type = "application/json-rpc; charset=utf-8"
  process_get_requests = True

  zpublisher_handled = False
  id = None

  def parse_request(self, request):
    # check whether this is should be handled via the standard ZPublisher
    #  If both "method" and "params" is present, we expect
    #  that "http://groups.google.com/group/json-rpc/web/json-rpc-over-http"
    #  applies.
    form = request.form
    if (is_standard_request(request)
        and not (form.get('method') is not None
             and form.get('params') is not None)
        ):
      self.zpublisher_handled = True
      return
    if form.get('method') is not None:
      # information provided via standard request parameters
      # Note: params is base64 encoded
      r = dict(
        method=form['method'],
        params=form.get(params, ()) and loads(form['params'].decode('base64')),
        id=form.get('id') and loads(request['id']),
        )
    else:
      # information provided in body
      r = loads(request['BODY'])
    # remember id for response generation
    self.id = r['id']
    # process parameters
    params = IDataAdapter(self).normalize_in(r['params'])
    args, kw = isinstance(params, list) and (params, {}) or ((), params)
    # jsonrpc.proxy uses '.' to structure -- convert to '/'
    method = r['method'].replace('.', '/')
    return method, args, kw

  def marshal_result(self, value):
    if not self.zpublisher_handled and self.id is None:
      # this has been a notification -- return a 204 response
      return None, 204
    return dumps(dict(
      result=IDataAdapter(self).normalize_out(value),
      error=None,
      id=self.id,
      ),
                 ensure_ascii=False)
    if not self.zpublisher_handled and self.id is None:
      # this has been a notification -- return a 204 response
      return None, 204
    return dumps(dict(
      result=IDataAdapter(self).normalize_out(value),
      error=None,
      id=self.id,
      ),
                 ensure_ascii=False)

  def marshal_exception(self, exc):
    if not self.zpublisher_handled and self.id is None:
      # this has been a notification -- return a 204 response
      return None, 204
    # ATT: we do not yet fully implement
    #  http://groups.google.com/group/json-rpc/web/json-rpc-over-http
    return dumps(dict(
      result=None,
      # this is from http://groups.google.com/group/json-rpc/web/json-rpc-2-0
      error=IDataAdapter(self).normalize_out(
        dict(code=IErrorCode(exc, -32603),
             message=IErrorMessage(exc, '%s: %s' % (str(exc.__class__), exc)),
             )
        ),
      id=self.id,
      ),
                 # Note: the spec seems to require code 500 but
                 #  the jsonrpc implementation expects 200
                 ensure_ascii=False)#, 500


class JsonDataAdapter(object):
  """mixin class to map our simple types not supported by json.

  Requires to be mixed together with a general data adapter.
  """

  def normalize_out(self, value):
    normalized = super(JsonDataAdapter, self).normalize_out(value)
    if isinstance(normalized, binary):
      # we map to "iso-8859-1" encoded unicode
      return normalized.decode('iso-8859-1')
    if isinstance(normalized, date):
      # we map to an ISO date string
      return normalized.strftime('%Y-%m-%d')
    if isinstance(normalized, datetime):
      # we map to an ISO datetime string
      return normalized.strftime('%Y-%m-%dT%H:%M:%S')
    return normalized


class StandardJsonDataAdapter(JsonDataAdapter, StandardDataAdapter): pass


class StandardJsonMarshaller(JsonMarshaller, StandardJsonDataAdapter):
  """``json`` marshaller combined with the ``StandardJsonDataAdapter``."""


# in fact a handler factory (as required for an adapter registration)
standard_json_handler = handlerfactory_from_marshaller(
  StandardJsonMarshaller()
  )
    


