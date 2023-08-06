# Copyright (C) 2010 by Dr. Dieter Maurer <dieter@handshake.de>; see 'LICENSE.txt' for details

from zope.interface import implements

from dm.zope.schema.schema import SchemaConfigured

from interfaces import IMarshaller


class MarshallerBase(SchemaConfigured):
  """abstract marshaller base class."""

  implements(IMarshaller)

  # to be defined by concrete classes
  def parse_request(self, request): raise NotImplementedError
  def marshal_result(self, value): raise NotImplementedError
  def marshal_exception(self, exc): raise NotImplementedError

  # for non communication marshallers
  def clone(self): return self


class CommunicatingMarshallerBase(MarshallerBase):
  def clone(self):
    from copy import copy
    return copy(self)



