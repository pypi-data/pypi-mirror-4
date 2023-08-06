# Copyright (C) 2010 by Dr. Dieter Maurer <dieter@handshake.de>; see 'LICENSE.txt' for details
"""jsonrpc proxy/client.

Essentially a fixed copy of http://json-rpc.org/browser/trunk/python-jsonrpc/jsonrpc/proxy.py.

For testing purposes. It is self contained and does not depend on
other things in this package.
"""
from urllib2 import Request, urlopen
from json import dumps, loads

class JSONRPCException(Exception):
  def __init__(self, rpcError):
    Exception.__init__(self)
    self.error = rpcError

class ServiceProxy(object):
  def __init__(self, serviceURL, serviceName=None):
    self.__serviceURL = serviceURL
    self.__serviceName = serviceName
	
  def __getattr__(self, name):
    if self.__serviceName != None:
      name = "%s.%s" % (self.__serviceName, name)
    return ServiceProxy(self.__serviceURL, name)
	
  def __call__(self, *args):
    postdata = dumps({"method": self.__serviceName, 'params': args, 'id':'jsonrpc'})
    r = Request(self.__serviceURL, postdata,
                {'Content-Type':'application/jsonrpc'},
                )
    respdata = urlopen(r).read()
    resp = loads(respdata)
    if resp['error'] != None:
      raise JSONRPCException(resp['error'])
    else:
      return resp['result']
