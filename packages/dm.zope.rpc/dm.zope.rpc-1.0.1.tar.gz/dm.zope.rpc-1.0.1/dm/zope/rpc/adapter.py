# Copyright (C) 2010 by Dr. Dieter Maurer <dieter@handshake.de>; see 'LICENSE.txt' for details
"""Standard data adapter."""
from sys import getdefaultencoding
from datetime import datetime, date
from codecs import lookup

from DateTime import DateTime
from zope.schema import Bool, TextLine
from zope.interface import implements, Interface

from dm.zope.schema.schema import SchemaConfigured

from interfaces import IDataAdapter, ISimpleExternalValue, ISimpleInternalValue
from type import binary


class IStandardDataAdapterSchema(Interface):
  text_uses_str = Bool(
    title=u"use Python's ``str`` to represent text",
    description=u"if this option is set, then convert incoming ``unicode`` to ``str`` and outgoing ``str`` to ``unicode`` using ``encoding`` (see below); otherwise, ``str`` is treated as binary data.",
    default=False,
    )

  encoding = TextLine(
    title=u"encoding to convert between ``str`` and ``unicode``",
    description=u"This can be either a codec or a utility name. In the latter case, a utility for this name is looked up and should give the encoding (not yet implemented). If the value is empty, then Python's default encoding is used.",
    default=u'',
    )

  use_zope_datetime = Bool(
    title=u"use Zope's ``DateTime`` to represent datetime values",
    description=u"This option controls whether Zope's ``DateTime`` or Python's ``datetime`` is used to represent incoming datetime values. On output, Zope's ``DateTime`` is always converted to Python's ``datetime``.",
    default=False,
    )


class StandardDataAdapter(SchemaConfigured):
  """a standard ``DataAdapter``."""

  implements(IStandardDataAdapterSchema, IDataAdapter)


  def normalize_in(self, external_value):
    v = external_value
    __traceback_info__ = v
    # try adapter
    adapted = ISimpleInternalValue(v, self)
    if adapted is not self: v = adapted
    if v is None: return
    if isinstance(v, (bool, int, float, binary)): return v
    if isinstance(v, str): # this should not happen
      if self.text_uses_str: return v
      else: return binary(v)
    if isinstance(v, unicode):
      if self.text_uses_str: return v.encode(self._get_encoding())
      else: return v
    if isinstance(v, date):
      if self.use_zope_datetime:
        args = v.year, v.month, v.day
        if isinstance(v, datetime):
          # do we need an option to control convertion to local time?
          args += (v.hour, v.minute, v.second, 'utc')
        return DateTime(*args)
      else: return v
    # recursive conversion
    n = self.normalize_in
    # see whether this is dict like
    # ATT: we do not normalize the keys (this might be a bug)
    if hasattr(v, 'items'): return _DictWrapper(v, n)
    # has it a ``__dict__``
    if hasattr(v, '__dict__'): return _DictWrapper(v, n)
    # see whether it is iterable
    if hasattr(v, '__iter__'): return map(n, v)
    raise NotImplementedError('cannot normalize: %s' %v)

  def normalize_out(self, internal_value):
    v = internal_value
    __traceback_info__ = v
    # try adapter
    adapted = ISimpleExternalValue(v, self)
    if adapted is not self: v = adapted
    if v is None: return
    if isinstance(v, (bool, int, float, binary, unicode, date)): return v
    if isinstance(v, str):
      if self.text_uses_str: return v.decode(self._get_encoding())
      else: return binary(v)
    if isinstance(v, DateTime):
      # this may be a date or a datetime
      #  we interpret is as date when hour, min and sec are all 0
      h, m, s = v.hour(), v.minute(), v.second()
      if h == m == s == 0:
        return date(v.year(), v.month(), v.day())
      # looks like a datetime -- convert to utc
      v = v.toZone('utc')
      return datetime(v.year(), v.month(), v.day(), v.hour(), v.minute(), int(v.second()))
    # recursive conversion
    # This is tricky:
    #  If it is a mapping, we convert to its items
    #  if it is iterable, we convert to the list of elements
    #  else we use its '__dict__' (removing private attributes)
    #  or fail
    n = self.normalize_out
    # if it has a __dict__, use it
    if hasattr(v, '__dict__') \
           and not (hasattr(v, 'items') or hasattr(v, '__iter__')):
      # do not pass on private attributes
      vd = v.__dict__
      vt = hasattr(v, '__class__') and v.__class__ or type(v)
      rpc_type = getattr(v, '_rpc_type', None)
      v = dict((k, vd[k]) for k in v.__dict__  if not k.startswith('_'))
      # pass on '_rpc_type' information
      v['_rpc_type'] = rpc_type or u'%s.%s' % (vt.__module__, vt.__name__)
    # if it is mapping like, return a dict
    if hasattr(v, 'items'):
      return dict((self.to_unicode(k), n(v)) for (k,v) in v.items())
    # see whether it is iterable
    if hasattr(v, '__iter__'): return map(n, v)
    raise NotImplementedError('cannot normalize: %s' %v)

  def to_unicode(self, v):
    if isinstance(v, unicode): return v
    if isinstance(v, str): return v.decode(self._get_encoding())
    return unicode(v)

  def _get_encoding(self):
    enc = self.encoding
    if not enc: return getdefaultencoding()
    try: lookup(enc); return enc
    except LookupError:
      raise NotImplementedError("""'%s' is not a registered encoding.
      Lookup via a utility is not yet implemented. Contact the author if
      you need this feature.""" % enc)


class _DictWrapper(dict):
  # allow unrestricted access from untrusted code
  __allow_access_to_unprotected_subobjects__ = 1
  __roles__ = ()
  _guarded_write = 1

  def __init__(self, v, normalize):
    vt = type(v)
    if hasattr(v, 'items'): items = v.items()
    else: items = v.__dict__.items()
    d = dict((k, normalize(v)) for (k,v) in items)
    if '_rpc_type' not in d and vt.__module__ != '__builtin__':
      d['_rpc_type'] = u'%s.%s' % (vt.__module__, vt.__name__)
    self.update(d)

  def __getattr__(self, k):
    try: return self[k]
    except KeyError: raise AttributeError(k)

  def __setattr__(self, k, v): self[k] = v

  def __delattr__(self, k):
    try: del self[k]
    except KeyError: raise AttributeError(k)

        
  
