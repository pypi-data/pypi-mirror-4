# Copyright (C) 2010 by Dr. Dieter Maurer <dieter@handshake.de>; see 'LICENSE.txt' for details
from zope.interface import Interface
from zope.schema import TextLine, Bool


class IProtocolHandler(Interface):
  """A handler for one or a set of rpc protocols.

  Usually integrated via a Zope Toolkit "namespace".
  """
  def __init__(context, request):
    """set up request and response to handle an rpc request.

    If the request has an entity, this is usually parsed
    to determine method, args and keyword args. The request
    is updated accordingly.

    In addition, a new response is set up that handles
    the result, either a normal result or an exception,
    and marshals it in a protocol conformant way.
    """

  def __of__(parent):
    """used by theZ ``ZPublisher``.

    Usually returns *parent*, maybe after setting additional request attributes.
    """


class IDataAdapter(Interface):
  """An adapter to normalize data values.

  Normalized values include ``int``, ``float``, ``boolean``,
  a text type, ``binary``, a datetime type, lists and objects of
  normalized values.

  Objects support both attribute and item access and the mapping interface.
  There are both readable and writable by untrusted code.

  Usually used as a Zope Toolkit adapter for the protocol handler,
  a Zope Toolkit utility or a universal default.
  """
  def normalize_in(external_value):
    """normalize *external_value* to be used internally.

    The text type can be either ``unicode`` or ``str``.
    The datetime type can be either ``datetime`` or Zope's ``DateTime`` (UTC).
    """

  def normalize_out(internal_value):
    """normalize *internal_value* to be used externally.

    The text type is always ``unicode``, the datetime type always ``datetime``.

    Objects (with a ``__dict__``) are normalized to dicts with all
    attributes starting with ``_`` removed.
    This can lose default attribute defined on class level.
    The normalization can be controlled by special attributes:

      ``_rpc_attributes``
      the list of relevant attributes; all other attributes are ignored.

      ``_rpc_inherit``
      a boolean, indicating that data values should be looked for in
      the class as well. This can be expensive.

    The normalization sets the key ``_rpc_type`` to the type name of
    the normalized value.
    """


class IErrorCode(Interface):
  """Used to adapt an exception into an error code."""


class IErrorMessage(Interface):
  """Used to adapt an exception into an error message."""


class ISimpleExternalValue(Interface):
  """indicats a simple external value.

  Usually used as an adapter.
  """


class ISimpleInternalValue(Interface):
  """indicated a simple internal value.

  Usually used as an adapter.
  """


class IMarshaller(Interface):
  """marshalling/demarshalling.
  
  Used by base protocol handler class and standard response for
  demarshalling or marshalling purposes, respectively.
  """

  content_type = TextLine(title=u"content type")

  process_get_requests = Bool(
    title=u"process_get_requests",
    description=u"indication that GET requests should be marshaller parsed.",
    default=False,
    )

  def parse_request(request):
    """parse the request and return ``None`` or triple *method*, *args* and *kw*.
    Returning ``None`` specifies that the standard ZPublisher
    publication should be used. This is mainly used for
    ``GET`` requests.
    
    *method* is the ("/" separated) path for the method to be called.
    *args* is a sequence of positional arguments and *kw* a mapping
    of keyword arguments.
    """

  def marshal_result(value):
    """marshal *value* as rpc result.

    Return either *entity* or a pair *entity*, *status*.
    *status* defaults to ``200``.
    """

  def marshal_exception(exc):
    """marshal *exc* as rpc exception.

    Return either *entity* or a pair *entity*, *status*.
    *status* defaults to ``200``.

    If ``marshal_exception`` raises an exception, then the
    exception is handled by the underlying (non-rpc) protocol.
    """

  def clone():
    """a marshaller clone.

    This allows marshallers to communicate between ``parse_request``
    and the ``marshal`` methods.

    Marshallers that do not need such communication can return itself.
    """

