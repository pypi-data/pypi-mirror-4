# Copyright (C) 2010 by Dr. Dieter Maurer <dieter@handshake.de>; see 'LICENSE.txt' for details
"""Standard namespace.

Zope Toolkit implements a namespace usually as both a view (multiadpater
of context and request) and an adapter (of context) providing
``zope.traversing.interfaces.ITraversable``.
In our case, the adapter does not make sense. The namespace implementation
below is designed only to be used as view.

It is expected to provide access to rpc protocol handlers. It looks them
up as ``IProtocolHandler`` views.
"""
from zope.interface import implements
from zope.component import getMultiAdapter
from zope.traversing.interfaces import ITraversable

from interfaces import IProtocolHandler


class RpcNamespace(object):
  implements(ITraversable)

  def __init__(self, context, request):
    self.context = context; self.request = request

  def traverse(self, name, further_path):
    return getMultiAdapter(
      (self.context, self.request), IProtocolHandler, name=name
      )

