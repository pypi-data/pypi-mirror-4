SockJSProxy
===========

SockJSProxy is a simple proxy server that proxies message from SockJS_ to a
ZeroMQ_ socket and vise-versa.

Motivation
----------

Implementing the SockJS protocol is not trivial, as it supports a handful of
transports. However, good `ZeroMQ bindings`_ exist for pretty much every popular
language. This simple proxy allows the use of Real-time web communication (via
SockJS_) for nearly every popular language.

Implementation
--------------

This proxy is implemeted in Python_ using the sockjs-tornado_ and pyzmq_ librries.
It uses the `Tornado Web Server`_, which is a non-blocking server and should
easily handle 1000s of clients.

ZeroMQ protocol
---------------

SockJSProxy uses a simple ZeroMQ multipart_-based message protocol to proxy messages.
You should implement the other end of this protocol, but that should be quite easy.


It `binds`_ to two sockets.

----------

The incomming messages socket is a ``PUSH`` one (by default on port ``9241``), where
the proxy will push messages to. All messages are 3-part messages in the form of:

+------------------+
| ``message_type`` |
+------------------+
| ``session_id``   |
+------------------+
| ``data``         |
+------------------+

``message_type`` can be one of these. The other arguments are described under each
``message_type``:

``connect``
    Sent when a client connects to the server. The ``session_id`` is set,
    while the ``data`` field is empty (but present in the message)
``disconnect``
    Sent when a client disconnects from the server. Like ``connect``,
    the ``session_id`` is set, but the ``data`` is empty.
``message``
    Sent when a client sends a message. The ``session_id`` is the sender's
    session and ``data`` contains the message (as bytes) from the client.

----------

The outgoing socket is a ``PULL`` one (by default on port ``9242``), where the
proxy will read messages and forward them to the SockJS client (usually a browser).

The format is like the one for incomming messages:

+------------------+
| ``message_type`` |
+------------------+
| ``session_id``   |
+------------------+
| ``data``         |
+------------------+

As of now the supported ``message_type`` are:

``message``
    Send this to forward a message to a client with ``session_id``.
    ``data`` contains the message (as bytes) for the client.
``disconnect``
    Disconnect the client with the given ``session_id``.
    ``data`` is discarded but *must* be present in the message as
    a part (usually empty).


Installation
------------

Installation is done like any other Python package: ``pip install sockjsproxy``.

Usage
-----

This proxy exposes a command ``sockjsproxy``. Here is the usage for it.

::

    usage: sockjsproxy [-h] [--version] [--address ADDRESS] [--in-port IN_PORT]
                       [--out-port OUT_PORT] [--http-port HTTP_PORT]
                       [--static-path STATIC_PATH] [--static-url STATIC_URL]
                       [--samples SAMPLES] [--verbose]

    Proxy messages between sock.js and a 0MQ socket

    optional arguments:
      -h, --help            show this help message and exit
      --version             show program's version number and exit
      --address ADDRESS, -a ADDRESS
                            The 0MQ address to listen to. Defaults to * (meaning -
                            everything)
      --in-port IN_PORT, -i IN_PORT
                            The port to listen for incoming 0MQ connections.
                            Defaults to 9241
      --out-port OUT_PORT, -o OUT_PORT
                            The port to listen for outgoing 0MQ connections.
                            Defaults to 9242
      --http-port HTTP_PORT, -p HTTP_PORT
                            The port to listen for http (sock.js) connections.
                            Defaults to 8080
      --static-path STATIC_PATH, -s STATIC_PATH
                            The path to a local static directory to be served
                            under --static-url
      --static-url STATIC_URL, -u STATIC_URL
                            The url where the files in --static-path will be
                            served
      --samples SAMPLES     Serve samples under SAMPLES path
      --verbose, -v         Make the server output more information - useful for
                            debugging


Samples
-------

The samples_ directory contains an example client_ and server_ that use the proxy.

Once installed, you can launch the proxy in one terminal with

::

    sockjsproxy --samples samples --verbose


and launch in another terminal

::

    datereply-sjp.py

Then visit ``http://localhost:8080/samples/``,
play with the demo, see the log output and play with the code.
This simple ``datereply-sjp.py`` script is a simple echo server,
that will reply with the current time to every message and force
the client to disconnect (by sending a ``disconnect`` message to
the proxy server).

Licence
-------
MIT

Authors
-------
- Emil Ivanov

Changelog
---------
0.7
  - Switch from ``PUB/SUB`` socket pair to ``PUSH/PULL``.
  - Add support to force the client to disconnect.


.. _Python: http://python.org/
.. _SockJS: https://github.com/sockjs/sockjs-client
.. _ZeroMQ: http://www.zeromq.org/
.. _ZeroMQ bindings: http://www.zeromq.org/bindings:_start
.. _sockjs-tornado: https://github.com/MrJoes/sockjs-tornado
.. _pyzmq: http://zeromq.github.com/pyzmq/
.. _Tornado Web Server: http://www.tornadoweb.org/
.. _binds: http://api.zeromq.org/2-1:zmq-bind
.. _multipart: http://api.zeromq.org/2-1:zmq-send#toc3
.. _samples: src/tip/sockjsproxy/samples
.. _client: src/tip/sockjsproxy/samples/index.html
.. _server: src/tip/sockjsproxy/samples/datereply-sjp.py