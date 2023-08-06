# Copyright (C) 2010 by Dr. Dieter Maurer <dieter@handshake.de>; see 'LICENSE.txt' for details
"""An rpc protocol based on Python's ``repr`` representation.

**ATTENTION: ** The use of its unmarshalling is highly unsafe. Use it only
with trusted clients.
"""
from zope.interface import implements, Interface
from zope.schema import Bool

from dm.zope.schema.schema import SchemaConfigured

from dm.zope.rpc.interfaces import IProtocolHandler, IMarshaller, IDataAdapter
from dm.zope.rpc.adapter import StandardDataAdapter
from dm.zope.rpc.marshaller import MarshallerBase
from dm.zope.rpc.handler import handlerfactory_from_marshaller

class IReprMarshaller(Interface):
  parse_request_entity = Bool(
    title=u"allow parsing a request entity",
    description=u"""Usually, this marshaller supports output only. Method and arguments of an rpc call must be passed in the standard HTTP way (url with request parameters).
    This option allows the parsing of a request entity. The entity must
    use Python's ``repr`` format and when evaled yield a tuple with 1 to 3
    components *method*, *args* and *kwargs*.
    Note that the ``eval`` use is dangerous. Therefore, the option should
    only be activated, when you can trust all potential clients.
    """,
    default=False)


class ReprMarshaller(MarshallerBase):
  """Generic ``repr`` marshaller."""
  implements(IReprMarshaller)

  content_type = "text/plain"

  def parse_request(self, request):
    if not self.parse_request_entity:
      raise NotImplementedError(
        'This protocol handler is configured to support only output. '
        'Use GET requests for this service.'
        )
    d = dict(__builtins__=None)
    r = eval(request['BODY'], d)
    if not isinstance(r, tuple) or len(r) > 3 or not r:
      raise ValueError('entity must contain a tuple with at least 1 and at most 3 elements')
    # fill with defaults
    r += (None, (), {})[len(r):]
    method, args, kw = IDataAdapter(self).normalize_in(r)
    method = str(method) # avoid unicode
    return method, args, kw

  def marshal_result(self, value):
    return repr(IDataAdapter(self).normalize_out(value))

  def marshal_exception(self, exc):
    raise NotImplementedError() # causes normal exception processing


class StandardReprMarshaller(ReprMarshaller, StandardDataAdapter):
  """``repr`` marshaller combined with the ``StandardDataAdapter``."""


# in fact a handler factory (as required for an adapter registration)
standard_repr_handler = handlerfactory_from_marshaller(
  StandardReprMarshaller()
  )
    


