"""
This module contains the backend controller
"""
import sys
from pyqode.core.api.client import JsonTcpClient
from pyqode.core.api.manager import Manager


class BackendManager(Manager):
    """
    The backend controller takes care of controlling the client-server
    architecture.

    It is responsible of starting the backend process and the client socket and
    exposes an API to easily control the backend:

        - start
        - stop
        - send_request

    """

    def __init__(self, editor):
        super().__init__(editor)
        #: client socket
        self.socket = JsonTcpClient(editor)

    def start(self, script, interpreter=sys.executable, args=None):
        """
        Starts the backend server process.

        The server is a python script that starts a
        :class:`pyqode.core.backend.JsonServer`. You must write the server
        script so that you can apply your own configuration on the server side.

        The script can be run with a custom interpreter. The default is to use
        sys.executable.

        :param script: Path to the server main script.
        :param interpreter: The python interpreter to use to run the server
            script. If None, sys.executable is used unless we are in a frozen
            application (frozen servers do not require an interpreter).
        :param args: list of additional command line args to use to start
            the server process.
        """
        self.socket.start(script, interpreter=interpreter, args=args)

    def stop(self):
        """
        Stop backend process (by terminating it).
        """
        try:
            if self.socket:
                self.socket.close()
        except RuntimeError:
            pass

    def send_request(self, worker_class_or_function, args, on_receive=None):
        """
        Request some work to be done server side. You can get notified of the
        work results by passing a callback (on_receive).

        :param: editor: editor instance
        :param worker_class_or_function: Worker class or function
        :param args: worker args, any Json serializable objects
        :param on_receive: an optional callback executed when we receive the
            worker's results. The callback will be called with two arguments:
            the status (bool) and the results (object)

        :raise: backend.NotConnected if the server cannot be reached.

        """
        self.socket.request_work(worker_class_or_function, args,
                                 on_receive=on_receive)

    @property
    def connected(self):
        """
        Checks if the client socket is connected to a backend server.

        """
        return self.socket.is_connected
