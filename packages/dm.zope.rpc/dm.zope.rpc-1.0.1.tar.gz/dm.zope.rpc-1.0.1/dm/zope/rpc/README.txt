This package implements a middleware
which allows to provide an internet
service (a set of functions made available via the internet)
over multiple rpc protocols with a common (protocol independent) service
implementation.

The service functions can be called both via "GET" as well as
"POST" requests. "GET" requests are supported to leverage HTTP caching and to
facilitate debugging. To get the types right, "GET" requests must use the
``ZPublisher`` type conversion support (or some "GET" support
defined by the rpc protocol itself (as e.g. by the json-rpc protocol)).

The rpc protocol can be selected via url components (other means
are implementable as well but not directly supported). Available protocols
are selectable via deployment configuration.

This package supports the protocols

 ``reprrpc`` 
   a result format based on Python's repr -- mainly for testing purposes,

 ``jsonrpc``
   a ``json`` based rpc protocol, defined by http://json-rpc.org/.

   This requires the ``json`` module of Python 2.6 (separately installed,
   if necessary)

 ``xmlrpc``
   the rpc protocol based on Python's ``xmlrpc`` module.

   This requires the PyPI package ``dm.reuse`` and
   (probably) ``dm.zopepatches.xmlrpc`` (to control/deactivate
   Zope's builtin xmlrpc support).

Forthcoming subpackages will support ``soap`` based protocols for
services described by WSDL.


Architecture
============

At the package's core is a protocol handler. Its task is to handle
incoming requests for a specific rpc protocol. To prepare for the
protocol specific serialization of the result, it installs a new
response object. This will handle the result and potential exceptions
in a protocol specific way. In addition, the handler parses a potential
request body and updates the ``ZPublisher`` argument information
accordingly. Thereafter, "GET" and "POST" requests are (almost) identical.

Usually, the protocol handlers for the various protocols are
registered in a Zope Toolkit ``namespace``. Protocol selection
then can use an url component of the form
``++``\ *namespace*\ ``++``\ *protocol*.

The protocol handlers in this package derive from a generic
(protocol and configuration independent) class and delegate protocol 
and configuration specific operations to a protocol specific mashaller,
which also holds the configuration. The marshaller is either
specified via the handler's ``marshaller`` attribute or obtained
by adaptation of the handler to the ``.interfaces.IMarshaller`` interface.
The function ``.handler.handlerfactory_from_marshaller`` facilitates
the definition of a handler factory which then can be used in the
definition of an adapter.
As a consequence, a specially configured protocol handler
is usually set up by instantiating an appropriately configured
marshaller, passing this marshaller to ``handlerfactory_from_marshaller``
and registering the resulting protocol handler factory as
an adapter (for context and request).

The rpc protocols usually support only a limited set of types.
The potentially richer type world used by the service results need
to be mapped to the restricted type set. In addition, the types
delivered by the protocol modules' deserialization differ. Using
a standardized set of types toward the service
facilitates its implementation.
Therefore, the architecture contains an ``IDataAdapter`` component.
It has two methods ``normalize_in`` and ``normalize_out`` to normalize
the types used in incoming or outgoing values, respectively.
The marshallers look it up via adaptation to ``.interfaces.IDataAdapter``.
The implemented marshallers derive from ``.adapter.StandardDataAdapter``.
It normalizes incoming types to ``bool``, ``int``, ``float``, ``binary``,
a text type (either ``str`` or ``unicode``), a date type
(either ``datetime.date`` or Zope's ``DateTime.DateTime``),
a datetime type (either ``datetime.datetime`` or Zope's ``DateTime.DateTime``)
and lists and structure wrappers of normalized types.
The structure wrappers support both the mapping api as well as
attribute access; they can be read and written by untrusted code.
Options control which text, date and datetime types are used (see below).
Outgoing types are normalized to ``bool``, ``int``, ``float``, ``binary``,
``unicode``, ``date``, ``datetime`` and lists/dictionaries of normalized
values. Instance objects with an ``items`` method are normalized
to the dicts of (normalized) items; instance objects with an ``__iter__``
method are normalized as the list of (normalized) iterated values;
other instance objects are normalized by normalizing their
``__dict__`` omitting attributes starting with ``_`` (priviate
attributes), an ``_rpc_type`` attribute may be added to convey
the original type. This has the drawback that default (class level
defined) attributes are not taken into account.
You can find details about the standard data adapter in 
``adapter.txt`` in the subdirectory ``tests``.

Text handling is difficult with rpc protocols.
With Python 2.x, ``str`` is still often used to represent both text
and binary data while many rpc protocols make a strict distinction
between text and binary data. Therefore, the package defines
a special type ``binary`` to clearly mark binary data.
``binary`` is derived from ``str`` and can (usually) be used whereever ``str``
is usable (there are a few exceptions).
An option for the standard data adapter specifies whether
the service uses ``str`` to represent text. In this case, the
protocol text type is mapped to ``str`` (and vice versa) using an encoding
specified via an additional option.
Some rpc protocols (e.g. ``json``) do not support a binary type. In this
case, the module assumes that binary data is coded by the first 256 unicode
codepoints. The ``binary`` type implements this assumption.

In the Zope [2] world, dates and datetimes pose another ambiguitiy.
Traditionally, Zope uses its ``DateTime.DateTime`` class to represent
dates and datetimes. But newer applications may have switched to Python's
new ``date`` and ``datetime`` types. The standard data adapter uses
Python's types to represent dates and times externally (toward the
protocol) and has an option whether it should convert them to
Zope's ``DateTime`` internally (toward the service implementation).


Examples
========

You can find simple examples in ``tests.example`` and ``tests.xmlrpc``.
``example`` demonstrates example zcml registrations to support
``jsonrpc`` and ``reprrpc``, ``xmlrpc`` does so for the ``xmlrpc`` protocol.

The package uses (mostly) the Zope Toolkit component architecture
to combine the various architectural components and
integrate the package into an application. This provides for great
flexibility. Individual components can be easily replaced by
application specific adaptations. Up to now, there are no
documentation or specific examples. You will need to look at
the component sources to find out the possibilities.

Installation
============

The package expects to be used inside a Zope [2] environment.
However, to facilitate use in a Zope below version 2.12 (the first eggified
Zope 2 version), it does not specify this dependency.

In a Zope below 2.12, it might be necessary to set up some
so called ``fake-eggs`` (supported by the buildout recipe
``plone.recipe.plone2instance``) or egg links, e.g. for ``zope.schema``,
and ``zope.interface``, such that these eggs are found inside the
Zope codetree.
