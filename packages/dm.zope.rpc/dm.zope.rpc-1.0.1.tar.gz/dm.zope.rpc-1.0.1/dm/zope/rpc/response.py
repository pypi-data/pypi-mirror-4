# Copyright (C) 2010 by Dr. Dieter Maurer <dieter@handshake.de>; see 'LICENSE.txt' for details
"""Standard response implementation."""
from sys import exc_info
from logging import getLogger

from AccessControl import Unauthorized

logger = getLogger('dm.zope.rpc.response')


class _IgnoreModification(object):
  """Auxiliary descriptor to ignore modifications."""

  def __init__(self, obj): self._obj = obj
  def __get__(self, *args): return self._obj
  def __set__(self, *args): pass

def _unauthorized(): raise Unauthorized


class Response(object):
  """Rpc mashalling response wrapping the original response.

  We essentially delegate to the original response (via ``__getattr__``).

  Because we modify the response too late to get it used consistently,
  we override (reflect) some of the original responese's methods to
  call instead us. This is done by ``_reflect``. ``_unreflect`` restores
  the original method.
  """

  # hopefully, this disables 'standard_error_message'
  #   if not, we need something that does
  _error_format = 'text/plain'

  # methods to be reflected (from original reponse to us)
  REFLECTED_METHODS = 'setBase setBody exception unauthorized'.split()

  _base = None
  _ori_response = None # to make '__getattr__' a bit safer
  _unreflected = True


  def __init__(self, response, marshaller):
    self._ori_response = response
    self._marshaller = marshaller
    self._reflect()

  def _reflect(self):
    ori = self._ori_response
    for m in self.REFLECTED_METHODS:
      setattr(self, '_ori_' + m, getattr(ori, m))
      setattr(ori, m, getattr(self, m))
    self._unreflected = False

  def _unreflect(self):
    self._unreflected = True
    ori = self._ori_response
    for m in self.REFLECTED_METHODS:
      setattr(ori, m, getattr(self, '_ori_' + m))

  def setBase(self, base):
    if self._unreflected: return self._ori_setBase(base)
    self._base = base

  def setBody(self, body):
    if self._unreflected: return self._ori_setBody(body)
    self._unreflect()
    self._result(result=body)

  def exception(self,  fatal=0, info=None):
    """see 'ZPublisher.BaseResponse'."""
    ori = self._ori_response
    if self._unreflected: ori.exception(fatal, info)
    self._unreflect()
    if info is None: info = exc_info()
    exc_class, exc_value = info[:2]
    from zExceptions import Unauthorized, Redirect, NotFound, Forbidden
    # some exceptions, we want to handle the standard way
    if (
      (isinstance(exc_class, str) # an ancient Zope still using string exceptions
       and exc_class in ('Unauthorized', 'Redirect', 'NotFound', 'Forbidden')
       )
      or isinstance(exc_value, (Unauthorized, Redirect, NotFound, Forbidden))
      ):
      return ori.exception(fatal, info)
    try:
      self._result(exc=exc_value)
    except:
      # if we fail to render the exception, we let the original response
      # try to handle it (to get any error indication at all)
      logger.exception('failed to marshal exception')
      ori.exception(fatal, info)

  # we do not want 'unauthorized' to be overridden (this is not adequate
  # for RPC). Therefore, we implement it as a property which ignores
  # modifications
  unauthorized = _IgnoreModification(_unauthorized)

  def _result(self, result=None, exc=None):
    """process the result.

    Either *result* or *exc* should be ``None``.
    """
    ori = self._ori_response
    marshaller = self._marshaller
    if exc is not None: r = marshaller.marshal_exception(exc)
    else: r= marshaller.marshal_result(result)
    entity, status = isinstance(r, tuple) and r or (r, 200)
    if self._base is not None: ori.setHeader('Content-Location', self._base)
    if status != 204:
      ori.setHeader('Content-Type', marshaller.content_type)
      ori.setBody(entity)
    ori.setStatus(status)


  def __getattr__(self, key):
    return getattr(self._ori_response, key)
    
    
  
