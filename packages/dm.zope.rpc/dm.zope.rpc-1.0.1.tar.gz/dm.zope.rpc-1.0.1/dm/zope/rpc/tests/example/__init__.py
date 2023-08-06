# Copyright (C) 2010 by Dr. Dieter Maurer <dieter@handshake.de>; see 'LICENSE.txt' for details
"""Example setup.

This example sets up a simple service with two functions ``echo1(v1)``
and ``echo2(v1,v2)`` and makes it available via ``repr`` and ``json``
rpc. It requires the ``json`` module from Python 2.6 (this may mean
Zope 2.12, or an earlier Zope version with a backported ``json``).

Protocol selection happens with ``++rpc++``\*name* url segments, e.g.
``.../++rpc++repr/echo1?v1=1`` calls ``echo1`` with firt paramater ``1``
requesting a response in the ``repr`` format.

To set things up, you need to include ``dm.zope.rpc.tests.example``
in your zcml setup.
"""
