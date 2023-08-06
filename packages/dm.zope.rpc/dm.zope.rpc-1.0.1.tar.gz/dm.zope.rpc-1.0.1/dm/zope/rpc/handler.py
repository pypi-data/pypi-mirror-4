# Copyright (C) 2010 by Dr. Dieter Maurer <dieter@handshake.de>; see 'LICENSE.txt' for details
"""Protocal handler base class."""
from zope.interface import implements
from Acquisition.interfaces import IAcquirer

from interfaces import IProtocolHandler, IMarshaller
from response import Response
from util import is_standard_request


# Python keywords -- copied from the 2.7.3 language documentation (section 2.3.1)
KEYWORDS = """and       del       from      not       while
as        elif      global    or        with
assert    else      if        pass      yield
break     except    import    print
class     exec      in        raise
continue  finally   is        return
def       for       lambda    try""".split()


class HandlerBase(object):
  """Protocol handler base class."""
  implements(IProtocolHandler, IAcquirer)

  # maybe overridden by derived classes
  Response = Response
  marshaller = None

  def __init__(self, context, request):
    # to provide typical view attributes
    self.context = context; self.request = request
    marshaller = self._get_marshaller()
    request['Response'] = request.response = \
                          self.Response(request.response, marshaller)
    if not marshaller.process_get_requests:
      if is_standard_request(request): return # already parsed
    # the marshaller should parse the request
    parsed = marshaller.parse_request(request)
    if parsed is None: return # standard ZPublisher handling
    method, args, kw = parsed
    if method:
      method = str(method) # avoid unicode (which Zope cannot handle)
      # "method" is in fact a path; split and add
      method = method.split('/'); method.reverse()
      request.path[0:0] = method; request._hacked_path = 1
    request.args = args
    # provide alternative names for Python keywords
    for k in kw.keys():
      if k in KEYWORDS: kw[k + "_"] = kw[k]
    request.form.update(kw); request.other.update(kw)

  def __of__(self, parent): return parent

  def _get_marshaller(self):
    m = self.marshaller
    if m is None: m = IMarshaller(self)
    return m.clone()


def handlerfactory_from_marshaller(marshaller, class_=HandlerBase):
  class HandlerFactory(class_): pass
  HandlerFactory.marshaller = marshaller

  return HandlerFactory
  
