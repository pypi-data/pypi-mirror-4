# Copyright (C) 2010 by Dr. Dieter Maurer <dieter@handshake.de>; see 'LICENSE.txt' for details
"""Type definitions."""



class binary(str):
  '''type to mark binary strings (for Python -- XML conversion).'''

  # Note from http://www.python.org/doc/essays/ppt/lwnyc2002/whatsnew22.ppt:
  #  "__new__" is a static method with class argument
  def __new__(cls, v):
    if isinstance(v, unicode):
      #We use the first 256 codepoints of unicode then to represent
      #binary data.
      v = v.encode('iso-8859-1')
    return super(binary, cls).__new__(cls, v)

  def __getitem__(self, k):
    return binary(super(binary, self).__getitem__(k))

  def __getslice__(self, *args):
    return binary(super(binary, self).__getslice__(*args))
  
  def __add__(self, other):
    return binary(super(binary, self).__add__(other))
  
  def __radd__(self, other):
    return binary(other + str(self))

  def __mul__(self, n):
    return binary(super(binary, self).__mul__(n))

  def __rmul__(self, n):
    return binary(super(binary, self).__rmul__(n))

  def join(self, l):
    return binary(super(binary, self).join(l))

  def replace(self, *args):
    return binary(super(binary, self).replace(*args))

  def split(self, *args):
    return [binary(s) for s in super(binary, self).split(*args)]

  def splitlines(self, *args):
    return [binary(s) for s in super(binary, self).splitlines(*args)]

  def translate(self, *args):
    return binary(super(binary, self).translate(*args))


def to_binary(text):
  """Some protocols do not support binary data.
  We use the first 256 codepoints of unicode then to represent
  binary data.
  This function recodes such representations.
  """
  if isinstance(text, unicode): return binary(text.encode('iso-8859-1'))
  return binary(text)
