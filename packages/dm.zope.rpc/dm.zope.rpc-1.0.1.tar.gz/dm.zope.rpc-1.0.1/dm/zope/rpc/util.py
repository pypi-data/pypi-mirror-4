# Copyright (C) 2010 by Dr. Dieter Maurer <dieter@handshake.de>; see 'LICENSE.txt' for details
from cgi import parse_header


def is_standard_request(request):
  """True, if this is a Zope standard request.

  A Zope standard request is a request for which Zope has parsed the
  arguments and provided them in ``form``.
  """
  if not request.get('CONTENT_TYPE'): return True# "GET" request
  ct, _ = parse_header(request['CONTENT_TYPE'])
  return ct in ('application/x-www-form-urlencoded', 'multipart/form-data')

