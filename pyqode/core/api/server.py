#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#The MIT License (MIT)
#
#Copyright (c) <2013-2014> <Colin Duquesnoy and others, see AUTHORS.txt>
#
#Permission is hereby granted, free of charge, to any person obtaining a copy
#of this software and associated documentation files (the "Software"), to deal
#in the Software without restriction, including without limitation the rights
#to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#copies of the Software, and to permit persons to whom the Software is
#furnished to do so, subject to the following conditions:
#
#The above copyright notice and this permission notice shall be included in
#all copies or substantial portions of the Software.
#
#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
#THE SOFTWARE.
#
"""
This module contains the api for implementing the pyqode server side
application.

pyqode uses a client-server architecture for running heavy tasks such as code
analysis, code completion,...

Protocol
--------

We use a worker based json messaging server based
on tcp sockets. Our protocol is very simple. Each message is made up of two
parts:
  - a header: simply contains the length of the payload
  - a payload: a json formatted string, the content of the message.

The json object depends on if this is a request or a responds.

Request
+++++++
For a request, the object will contains the following fields:

  - 'request_id': uuid generated client side
  - 'worker': fully qualified name to the worker callable (class or function),
    e.g. 'pyqode.core.api.server.echo'
  - 'data': data specific to the chose worker.

E.g::

    {
        'worker': 'pyqode.core.api.workers.echo',
        'request_id': 'a97285af-cc88-48a4-ac69-7459b9c7fa66',
        'data': ('some code', 0)
    }

Response
++++++++

For a response, the object will contains the following fields:
    - 'request_id': uuid generated client side
    - 'status': worker status, boolean
    - 'results': worker results (list, tuple, string,...)

E.g::

    {
        'results': ['some code', 0],
        'status': True, 'request_id':
        'a97285af-cc88-48a4-ac69-7459b9c7fa66'
    }

Server script
~~~~~~~~~~~~~

The server script must be written by the user. Don't worry its very simple,
all you have to do is to create and run the JsonTcpServer. We choose to let
you write the main script to let you easily configure it. Some worker will
requires some tweaking (for the completion worker, you will want to add custom
completion providers, you might also want to modify sys.path,...). It also
makes the packaging process more consistent, your script will be packaged on
linux using setup.py and will be frozen on windows using cx_Freeze.

Here is the most simple and basic example of a server script:

.. code-block: python
    from pyqode.core.api import server

    if __name__ == '__main__':
        server.run()

.. warning:: The user can choose the python interpreter that will run the
    server. That means that classes and functions that run server side (
    workers) **should fully support python2 syntax!**

.. note:: print statements on the server side will be logged as debug messages
    on the client side. To have your messages logged as error message, use
    sys.stderr instead of print.
"""
import argparse
import inspect
import logging
import json
import struct
import sys
import traceback
import select

try:
    import socketserver
    _py33 = True
except ImportError:
    import SocketServer as socketserver
    _py33 = False


class JsonServer(socketserver.TCPServer):
    """
    A server socket based on a json messaging system.
    """
    class _Handler(socketserver.BaseRequestHandler):
        """
        Our custom request handler. There will always be only 1 request that
        establish the communication, this is a 1 to 1.

        Once the connection has been establish will loop forever waiting for
        pending command or for the shutdown signal.

        The handler also implements all the logic for packing/unpacking
        messages and calling the requested worker instance.
        """

        def read_bytes(self, size):
            if _py33:
                data = bytes()
            else:
                data = ''
            while len(data) < size:
                tmp = self.request.recv(size-len(data))
                data += tmp
                if tmp == '':
                    raise RuntimeError("socket connection broken")
            return data

        def get_msg_len(self):
            d = self.read_bytes(4)
            s = struct.unpack('=I', d)
            return s[0]

        def read(self):
            """
            Reads a json string from socket and load it.
            """
            size = self.get_msg_len()
            data = self.read_bytes(size).decode('utf-8')
            return json.loads(data)

        def send(self, obj):
            """
            Sends a python obj as a json string on the socket

            :param obj: The object to send, must be Json serializable.
            """
            msg = json.dumps(obj).encode('utf-8')
            header = struct.pack('=I', len(msg))
            self.request.sendall(header)
            self.request.sendall(msg)

        def handle(self):
            while True:
                data = self.read()
                self._handle(data)

        def _import_class(self, cl):
            """
            Imports a class from a fully qualified name string.

            :param cl: class string, e.g.
                "pyqode.core.modes.code_completion.Worker"
            :return: The corresponding class
            """
            d = cl.rfind(".")
            classname = cl[d+1:len(cl)]
            try:
                m = __import__(cl[0:d], globals(), locals(), [classname])
                klass = getattr(m, classname)
            except (ImportError, AttributeError):
                raise ImportError(cl)
            else:
                return klass

        def _handle(self, data):
            try:
                print('request received: %r' % data)
                assert data['worker']
                assert data['request_id']
                assert data['data']
                worker = self._import_class(data['worker'])
                if inspect.isclass(worker):
                    worker = worker()
                status, result = worker(data['data'])
                response = {'request_id': data['request_id'],
                            'status': status,
                            'results': result}
                print('sending response: %r' % response)
                self.send(response)
            except :
                e1, e2, e3 = sys.exc_info()
                traceback.print_exception(e1, e2, e3, file=sys.stderr)

    def __init__(self, args=None):
        """
        :param args: Argument parser args. If None, the server will setup and
            use its own argument parser (using
            :meth:`pyqode.core.api.server.default_parser`)
        """
        if not args:
            args = default_parser().parse_args()
        self.port = args.port
        self._shutdown_request = False
        # print('server running on port %s' % args.port)
        socketserver.TCPServer.__init__(
            self, ('127.0.0.1', int(args.port)), self._Handler)


def default_parser():
    """
    Configures and return the default argument parser. You should use this
    parser as a base if you want to add custom arguments.

    The default parser only has one argument, the tcp port used to start the
    server socket. *(QCodeEdit picks up a free port and use it to run
    the server and connect its client socket)*

    :returns: The default server argument parser.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("port", help="the local tcp port to use to run "
                        "the server")
    return parser


def run(args=None):
    """
    Creates the server and serves forever

    :param args: Optional argparser args if you decided to setup your own
        argument parser. Default is None to let the JsonServer setup its own
        parser and parse command line arguments.
    """
    server = JsonServer(args=args)
    server.serve_forever()


# Server script example
if __name__ == '__main__':
    import sys
    print("running with python %d.%d.%d" % (sys.version_info[:3]))
    run()
