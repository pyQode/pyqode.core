"""
This module contains the public API for interacting with the pyqode server
client side. It is made up of 3 functions:

    - start_server()
    - stop_server()
    - request_work()

"""
import sys


class NotConnectedError(Exception):
    """
    Raised if the client is not connected to the server when an operation is
    requested.
    """
    def __init__(self):
        super(NotConnectedError, self).__init__(
            'Client socket not connected or server not started')


def start_server(editor, script, interpreter=sys.executable, args=None):
    """
    Starts a pyqode server, specific to a QCodeEdit instance.

    The server is a python script that starts a
    :class:`pyqode.core.server.JsonServer`. You (the user) must write
    the server script so that you can apply your own configuration
    server side.

    The script can be run with a custom interpreter. The default is to use
    sys.executable.

    :param: editor: QCodeEdit instance
    :param str script: Path to the server main script.
    :param str interpreter: The python interpreter to use to run the server
        script. If None, sys.executable is used unless we are in a frozen
        application (cx_Freeze). The executable is not used if the
        executable scripts ends with '.exe' on Windows
    :param list args: list of additional command line args to use to start
        the server process.
    """
    editor._client.start(script, interpreter=interpreter, args=args)


def stop_server(editor):
    """
    Stops the server process for a specific QCodeEdit and closes the
    associated client socket.

    It is automatically called when the widgets is destroyed but you should
    rather close it explicitly.

    :param: editor: QCodeEdit instance
    """
    try:
        if editor._client:
            editor._client.close()
    except RuntimeError:
        pass


def request_work(editor, worker_class_or_function, args, on_receive=None):
    """
    Requests some work on the server process of a specific QCodeEdit instance.

    :param: editor: QCodeEdit instance
    :param worker_class_or_function: Worker class or function
    :param args: worker args, any Json serializable objects
    :param on_receive: an optional callback executed when we receive the
        worker's results. The callback will be called with two arguments:
        the status (bool) and the results (object)

    :raise: NotConnectedError if the server cannot be reached.

    """
    editor._client.request_work(worker_class_or_function, args,
                                on_receive=on_receive)
