# Copyright (C) 2010 by Dr. Dieter Maurer <dieter@handshake.de>; see 'LICENSE.txt' for details
"""Example xmlrpc use.

Note: it makes use of the PyPI packages ``dm.reuse``
(requirement of ``..protocol.xmlrpc``) and ``dm.zopepatches.xmlrpc``
(to deactivate Zope's builtin xmlrpc support).
"""

# deactivate Zope's xmlrpc support
from zope.interface import alsoProvides
from dm.zopepatches.xmlrpc.publisher.interfaces import IXmlrpcChecker

def no_zope_xmlrpc(request): return False
alsoProvides(no_zope_xmlrpc, IXmlrpcChecker)
