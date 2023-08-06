# Copyright (C) 2010 by Dr. Dieter Maurer <dieter@handshake.de>; see 'LICENSE.txt' for details

from datetime import date, datetime
from Products.Five.browser import BrowserView

class Service(BrowserView):
  """Example service implementation.

  Implementing the service via a browser view is one of infinitely
  many ways.
  """
  
  def echo1(self, v1):
    """echo with one argument."""
    return v1

  def echo2(self, v1, v2):
    """echo with two arguments."""
    return (v1, v2)

  def exception(self):
    """some exception"""
    raise NotImplementedError()

  def now_and_today(self):
    """return ``now`` and ``today``."""
    return datetime.now(), date.today()
