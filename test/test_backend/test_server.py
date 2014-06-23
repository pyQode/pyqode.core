import os
import sys
from pyqode.core.api.client import JsonTcpClient as JsonTcpClient
from pyqode.core.backend import server
from threading import Timer

from subprocess import Popen


process = None

port = None


def test_default_parser():
    assert server.default_parser() is not None


def run_client_process():
    global process, port
    wd = os.path.join(os.getcwd(), 'test', 'test_backend')
    script = os.path.join(wd, 'cli.py')
    process = Popen([sys.executable, script, port], cwd=wd)


def test_json_server():
    global port

    import select

    class Args:
        port = 6789

    argv = list(sys.argv)
    srv = server.JsonServer(args=Args())
    srv.server_close()

    port = str(JsonTcpClient.pick_free_port())

    sys.argv[:] = []
    sys.argv.append('server.py')
    sys.argv.append(port)
    srv = server.JsonServer()
    Timer(10, srv.server_close).start()
    Timer(1, run_client_process).start()
    try:
        srv.serve_forever()
    except (ValueError, select.error):
        pass  # when closed from client we have a ValueError because of a
              # bad file descriptior, this is not a bug in pyqode but in
              # socketserver
