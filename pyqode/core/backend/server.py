# -*- coding: utf-8 -*-
"""
This module contains the server socket definition.
"""
import argparse
import inspect
import logging
import json
import struct
import sys
import traceback
try:
    import socketserver
    PY33 = True
except ImportError:
    import SocketServer as socketserver
    PY33 = False


def _logger():
    """ Returns the module's logger """
    return logging.getLogger(__name__)


def import_class(klass):
    """
    Imports a class from a fully qualified name string.

    :param klass: class string, e.g.
        "pyqode.core.backend.workers.CodeCompletionWorker"
    :return: The corresponding class

    """
    path = klass.rfind(".")
    class_name = klass[path + 1: len(klass)]
    try:
        module = __import__(klass[0:path], globals(), locals(), [class_name])
        klass = getattr(module, class_name)
    except ImportError:
        raise ImportError(klass)
    except AttributeError:
        raise ImportError(klass)
    else:
        return klass


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
            """ Read x bytes """
            if not PY33:
                data = ''
            else:
                data = bytes()
            while len(data) < size:
                tmp = self.request.recv(size - len(data))
                data += tmp
                if tmp == '':
                    raise RuntimeError("socket connection broken")
            return data

        def get_msg_len(self):
            """ Gets message len """
            data = self.read_bytes(4)
            payload = struct.unpack('=I', data)
            return payload[0]

        def read(self):
            """ Reads a json string from socket and load it. """
            size = self.get_msg_len()
            data = self.read_bytes(size).decode('utf-8')
            return json.loads(data)

        def send(self, obj):
            """
            Sends a python obj as a json string on the socket.

            :param obj: The object to send, must be Json serializable.
            """
            msg = json.dumps(obj).encode('utf-8')
            print('sending %d bytes for the payload' % len(msg))
            header = struct.pack('=I', len(msg))
            self.request.sendall(header)
            self.request.sendall(msg)

        def handle(self):
            """
            Hanlde the request and keep it alive while shutdown signal
            has not been received
            """
            running = True
            while running:
                print('waiting for data')
                data = self.read()
                running = self._handle(data)
            print('server finished')
            self.srv.t = logging.threading.Thread(name='shutdown',
                                                  target=self.srv.shutdown)
            self.srv.t.start()

        def _handle(self, data):
            """
            Handles a work request.
            """
            try:
                print('handling request %r' % data)
                if data == 'shutdown':
                    print('shutdown request received')
                    return False
                assert data['worker']
                assert data['request_id']
                assert data['data']
                worker = import_class(data['worker'])
                if inspect.isclass(worker):
                    worker = worker()
                print('worker: %r' % worker)
                status, result = worker(data['data'])
                response = {'request_id': data['request_id'],
                            'status': status,
                            'results': result}
                print('sending response: %r' % response)
                self.send(response)
            except:
                print('error with data=%r' % data)
                exc1, exc2, exc3 = sys.exc_info()
                traceback.print_exception(exc1, exc2, exc3, file=sys.stderr)
            return True

    def __init__(self, args=None):
        """
        :param args: Argument parser args. If None, the server will setup and
            use its own argument parser (using
            :meth:`pyqode.core.backend.default_parser`)
        """
        if not args:
            args = default_parser().parse_args()
        self.port = args.port
        self._shutdown_request = False
        self._Handler.srv = self
        self._running = True
        # print('server running on port %s' % args.port)
        socketserver.TCPServer.__init__(
            self, ('127.0.0.1', int(args.port)), self._Handler)
        print('started on 127.0.0.1:%d' % int(args.port))
        print("running with python %d.%d.%d" % (sys.version_info[:3]))


def default_parser():
    """
    Configures and return the default argument parser. You should use this
    parser as a base if you want to add custom arguments.

    The default parser only has one argument, the tcp port used to start the
    server socket. *(CodeEdit picks up a free port and use it to run
    the server and connect its client socket)*

    :returns: The default server argument parser.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("port", help="the local tcp port to use to run "
                        "the server")
    return parser


def serve_forever(args=None):
    """
    Creates the server and serves forever

    :param args: Optional args if you decided to use your own
        argument parser. Default is None to let the JsonServer setup its own
        parser and parse command line arguments.
    """
    server = JsonServer(args=args)
    try:
        server.serve_forever()
    except ValueError:
        pass


# Server script example
if __name__ == '__main__':
    serve_forever()
