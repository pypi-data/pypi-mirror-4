# Copyright (C) 2010 by Dr. Dieter Maurer <dieter@handshake.de>; see 'LICENSE.txt' for details
"""An rpc protocol based on Python's ``xmlrpclib``.

It implements http://www.xmlrpc.com/spec with additional types
supported by Python's ``xmlrpclib``.

This module requires the package ``dm.reuse`` (installable from PyPI).

It is likely that you need ``dm.zopepatches.xmlrpc`` (properly configured)
to prevent Zope's (partially broken) xmlrpc support to take over.
Surprising effects will happen when both Zope's standard
xmlrpc support and this one are used together.
"""
from datetime import date, datetime
from xmlrpclib import loads, dumps, getparser, \
     Fault, Binary, \
     Unmarshaller as PyUnmarshaller, Marshaller as PyMarshaller

from dm.reuse import rebindFunction

from dm.zope.rpc.interfaces import \
     IProtocolHandler, IMarshaller, IDataAdapter, \
     IErrorCode, IErrorMessage
from dm.zope.rpc.adapter import StandardDataAdapter
from dm.zope.rpc.marshaller import MarshallerBase
from dm.zope.rpc.handler import handlerfactory_from_marshaller
from dm.zope.rpc.type import binary


class XmlMarshaller(MarshallerBase):
  """Generic xml-rpc marshaller."""

  content_type = "text/xml; charset=utf-8"

  def parse_request(self, request):
    args, method = IDataAdapter(self).normalize_in(
      loads(request['BODY'])
      )
    # map '.' to '/'
    if method: method = method.replace('.', '/')
    return method, args, {}

  def marshal_result(self, value):
    return self._marshal((IDataAdapter(self).normalize_out(value),))

  def marshal_exception(self, exc):
    return self._marshal(Fault(
      IErrorCode(exc, -32603), # should be an integer
      self.to_unicode(
        IErrorMessage(exc, '%s: %s' % (str(exc.__class__), exc))
        ),
      ))

  def to_unicode(self, error):
    """convert *error* to unicode.

    This implementation uses Python's defaultencoding assuming
    that error messages are either unicode or coded with the
    default encoding. You must override the method if these
    conditions are not met.
    """
    if not isinstance(error, unicode): error = unicode(error)
    return error

  def _marshal(self, result):
    __traceback_info__ = result
    return dumps(result, methodresponse=True)


class XmlDataAdapter(object):
  """Map between our ``binary`` and xmlrpclib's ``Binary``."""
  def normalize_in(self, value):
    if isinstance(value, Binary): return binary(value)
    return super(XmlDataAdapter, self).normalize_in(value)

  def normalize_out(self, value):
    norm = super(XmlDataAdapter, self).normalize_out(value)
    if isinstance(norm, binary): return Binary(norm)
    return norm


class StandardXmlDataAdapter(XmlDataAdapter, StandardDataAdapter): pass


class StandardXmlMarshaller(XmlMarshaller, StandardXmlDataAdapter):
  """``xmlrpc`` marshaller combined with ``StandardXmlDataAdapter``."""


standard_xml_handler = handlerfactory_from_marshaller(
  StandardXmlMarshaller()
  )


# xmlrpclib fixups and version normalization
class Unmarshaller(PyUnmarshaller):
  """the Python implementation converts unicode containing ascii only to ``str``
  and thus destroys type information. Get rid of this stupidity.
  """
  dispatch = PyUnmarshaller.dispatch.copy()

  def end_string(self, data):
    if not isinstance(data, unicode): data = unicode(data, self._encoding)
    self.append(data)
    self._value = 0
  dispatch["string"] = dispatch["name"] = end_string

class Marshaller(PyMarshaller):
  """the Python implementation forgets to handle ``date``. Fix this."""
  dispatch = PyMarshaller.dispatch.copy()

  def dump_date(self, value, write):
    return self.dump_datetime(
      datetime(value.year, value.month, value.day), write
      )
  dispatch[date] = dump_date

dumps = rebindFunction(dumps,
                       FastMarshaller=False,
                       Marshaller=Marshaller,
                       )

getparser = rebindFunction(getparser,
                           FastUnmarshaller=False,
                           Unmarshaller=Unmarshaller,
                           )

from inspect import getargspec
args, _, _, _ = getargspec(loads)
if 'use_datetime' in args:
  # this is a modern "xmlrpclib"
  loads = rebindFunction(loads, getparser=getparser,
                         argRebindDir=dict(use_datetime=True),
                         )
else:
  # this is an old style "xmlrpclib" without support for Python's "datetime"
  # add it
  from time import strptime
  from xmlrpclib import Marshaller as PyMarshaller

  loads = rebindFunction(loads, getparser=getparser)

  def end_dateTime(self, data):
    t = strptime(data, "%Y%m%dT%H:%M:%S")
    return datetime.datetime(*tuple(t)[:6])
  Unmarshaller.end_dateTime = Unmarshaller.dispatch["dateTime.iso8601"] \
                              = end_dateTime

  def dump_datetime(self, value, write):
    write("<value><dateTime.iso8601>")
    write("%04d%02d%02dT%02d:%02d:%02d" % (
      value.year, value.month, value.day,
      value.hour, value.minute, value.second
      ))
    write("</dateTime.iso8601></value>\n")
  Marshaller.dump_datetime = Marshaller.dispatch[datetime] = dump_datetime
    

