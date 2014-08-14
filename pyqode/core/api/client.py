"""
This module contains the client socket API. This API is exposed to the
user throught the backend manager (
:class:`pyqode.core.managers.BackendManager`)

"""
import json
import logging
import socket
import struct
import sys
import uuid
from pyqode.qt import QtCore, QtNetwork
from pyqode.core.backend import NotConnected


def _logger():
    return logging.getLogger(__name__)


#: Dictionary of socket errors messages
SOCKET_ERROR_STRINGS = {
    0: 'the connection was refused by the peer (or timed out).',
    1: 'the remote host closed the connection.',
    2: 'the host address was not found.',
    3: 'the socket operation failed because the application lacked the '
       'required privileges.',
    4: 'the local system ran out of resources (e.g., too many sockets).',
    5: 'the socket operation timed out.',
    6: "the datagram was larger than the operating system's limit (which can "
       "be as low as 8192 bytes).",
    7: 'an error occurred with the network (e.g., the network cable was '
       'accidentally plugged out).',
    # 9 and 10 are UDP only, we only care about TCP.
    # all others erros are unlikely to happen in our case (proxy related
    # errors)
    - 1: 'an unidentified error occurred.',
}

#: Dictionary of process errors messages
PROCESS_ERROR_STRING = {
    0: 'the process failed to start. Either the invoked program is missing, '
       'or you may have insufficient permissions to invoke the program.',
    1: 'the process crashed some time after starting successfully.',
    2: 'the last waitFor...() function timed out. The state of QProcess is '
       'unchanged, and you can try calling waitFor...() again.',
    4: 'an error occurred when attempting to write to the process. '
       'For example, the process may not be running, or it may have closed '
       'its input channel.',
    3: 'an error occurred when attempting to read from the process. '
       'For example, the process may not be running.',
    5: 'an unknown error occurred. This is the default return value of '
       'error().'
}


#: Delay before retrying to connect to server [ms]
TIMEOUT_BEFORE_RETRY = 100
#: Max retry
MAX_RETRY = 100


class JsonTcpClient(QtNetwork.QTcpSocket):
    """
    A json tcp client socket used to start and communicate with the pyqode
    server.

    It uses a simple message protocol. A message is made up of two parts.
    parts:
      - header: contains the length of the payload. (4bytes)
      - payload: data as a json string.

    """

    def __init__(self, parent):
        super().__init__(parent)
        self._port = -1
        self.connected.connect(self._on_connected)
        self.error.connect(self._on_error)
        self.disconnected.connect(self._on_disconnected)
        self.readyRead.connect(self._on_ready_read)
        self._header_complete = False
        self._header_buf = bytes()
        self._to_read = 0
        self._data_buf = bytes()
        #: associate request uuid with a callback, popped once executed
        self._callbacks = {}
        self.is_connected = False
        self._process = None
        self._connection_attempts = 0

    def _terminate_server_process(self):
        """ Terminates the server process """
        _logger().debug('terminating backend process')
        self._process.terminate()

    def close(self):
        """ Closes the socket and terminates the server process. """
        try:
            if self._process and self._process.running:
                if self.is_connected:
                    # send shutdown request
                    self.send('shutdown')
                if self._process and self._process.running:
                    self._terminate_server_process()
                    self.is_connected = False
                super().close()
                _logger().info('process terminated')
        except (AttributeError, RuntimeError):
            pass

    def start(self, server_script, interpreter=sys.executable, args=None,
              port=None):
        """
        Starts a pyqode server (and connect our client socket when the server
        process has started). The server is started with a random free port
        on local host (the port number is defined by command line args).

        The server is a python script that starts a
        :class:`pyqode.core.backend.server.JsonServer`. You (the user) must
        write the server script so that you can apply your own configuration
        server side.

        The script can be run with a custom interpreter. The default is to use
        sys.executable.

        :param str server_script: Path to the server main script.
        :param str interpreter: The python interpreter to use to run the server
            script. If None, sys.executable is used unless we are in a frozen
            application (cx_Freeze). The executable is not used if the
            executable scripts ends with '.exe' on Windows
        :param list args: list of additional command line args to use to start
            the server process.

        """
        major, minor, build = sys.version_info[:3]
        _logger().debug('running with python %d.%d.%d', major, minor, build)
        self._process = _ServerProcess(self.parent())
        self._process.started.connect(self._on_process_started)
        if not port:
            self._port = self.pick_free_port()
        else:
            self._port = port
        if hasattr(sys, "frozen") and not server_script.endswith('.py'):
            # frozen server script on windows/mac does not need an interpreter
            program = server_script
            pgm_args = [str(self._port)]
        else:
            program = interpreter
            pgm_args = [server_script, str(self._port)]
        if args:
            pgm_args += args
        self._process.start(program, pgm_args)
        _logger().info('starting server process: %s %s', program,
                       ' '.join(pgm_args))

    def request_work(self, worker_class_or_function, args, on_receive=None):
        """
        Requests a work on the server.

        :param worker_class_or_function: Class or function to execute remotely.
        :param args: worker args, any Json serializable objects
        :param on_receive: an optional callback executed when we receive the
            worker's results. The callback will be called with two arguments:
            the status (bool) and the results (object)

        :raise: BackendController.NotConnected if the server cannot
            be reached.
        """
        if not self._process or not self._process.running or \
                not self.is_connected:
            raise NotConnected()
        classname = '%s.%s' % (worker_class_or_function.__module__,
                               worker_class_or_function.__name__)
        request_id = str(uuid.uuid4())
        if on_receive:
            self._callbacks[request_id] = on_receive
        self.send({'request_id': request_id, 'worker': classname,
                   'data': args})

    def send(self, obj, encoding='utf-8'):
        """
        Sends a python object to the server. The object must be JSON
        serialisable.

        :param obj: object to send
        :param encoding: encoding used to encode the json message into a
            bytes array, this should match CodeEdit.file.encoding.
        """
        _logger().debug('sending request: %r', obj)
        msg = json.dumps(obj)
        msg = msg.encode(encoding)
        header = struct.pack('=I', len(msg))
        self.write(header)
        self.write(msg)

    def _on_process_started(self):
        """ Runs a timer to try to connect the server process """
        # give time to the server to starts its socket
        QtCore.QTimer.singleShot(TIMEOUT_BEFORE_RETRY, self._connect)

    @staticmethod
    def pick_free_port():
        """ Picks a free port """
        test_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        test_socket.bind(('127.0.0.1', 0))
        free_port = int(test_socket.getsockname()[1])
        test_socket.close()
        return free_port

    def _connect(self):
        """ Connects our client socket to the server socket """
        _logger().debug('connecting to 127.0.0.1:%d', self._port)
        self._connection_attempts += 1
        address = QtNetwork.QHostAddress('127.0.0.1')
        self.connectToHost(address, self._port)

    def _on_connected(self):
        """ Logs connected """
        _logger().info('connected to server: %s:%d',
                       self.peerName(), self.peerPort())
        self.is_connected = True

    def _on_error(self, error):
        """
        Logs socket error, retry connecting if error is
        ConnectionRefusedError
        """
        if error not in SOCKET_ERROR_STRINGS:  # pragma: no cover
            error = -1
        log_fct = _logger().error
        if error == 0:
            # not connected, log it as an info as it happens all the time on
            # slow machine (the time for the server to run)
            log_fct = _logger().info
        log_fct('socket error %d: %s', error, SOCKET_ERROR_STRINGS[error])
        if error == QtNetwork.QAbstractSocket.ConnectionRefusedError:
            # try again, sometimes the server process might not have started
            # its socket yet.
            if self._connection_attempts < MAX_RETRY:
                QtCore.QTimer.singleShot(TIMEOUT_BEFORE_RETRY, self._connect)
            else:
                raise RuntimeError('Failed to connect to the server after 100 '
                                   'unsuccessful attempts.')

    def _on_disconnected(self):
        """ Logs disconnected """
        try:
            _logger().info('disconnected from server: %s:%d',
                           self.peerName(), self.peerPort())
        except (AttributeError, RuntimeError):
            # logger might be None if for some reason qt deletes the socket
            # after python global exit
            pass
        try:
            self.is_connected = False
        except AttributeError:
            pass

    def _read_header(self):
        """ Reads message header """
        _logger().debug('reading header')
        self._header_buf += self.read(4)
        if len(self._header_buf) == 4:
            self._header_complete = True
            try:
                header = struct.unpack('=I', self._header_buf)
            except TypeError:
                # pyside
                header = struct.unpack('=I', self._header_buf.data())
            self._to_read = header[0]
            self._header_buf = bytes()
            _logger().debug('header content: %d', self._to_read)

    def _read_payload(self):
        """ Reads the payload (=data) """
        _logger().debug('reading payload data')
        _logger().debug('remaining bytes to read: %d', self._to_read)
        data_read = self.read(self._to_read)
        nb_bytes_read = len(data_read)
        _logger().debug('%d bytes read', nb_bytes_read)
        self._data_buf += data_read
        self._to_read -= nb_bytes_read
        if self._to_read <= 0:
            try:
                data = self._data_buf.decode('utf-8')
            except AttributeError:
                data = bytes(self._data_buf.data()).decode('utf-8')
            _logger().debug('payload read: %r', data)
            _logger().debug('payload length: %r', len(self._data_buf))
            _logger().debug('decoding payload as json object')
            obj = json.loads(data)
            _logger().debug('response received: %r', obj)
            request_id = obj['request_id']
            results = obj['results']
            status = obj['status']
            # possible callback
            if request_id in self._callbacks:
                callback = self._callbacks.pop(request_id)
                callback(status, results)
            self._header_complete = False
            self._data_buf = bytes()

    def _on_ready_read(self):
        """ Read bytes when ready read """
        while self.bytesAvailable():
            if not self._header_complete:
                self._read_header()
            else:
                self._read_payload()


class _ServerProcess(QtCore.QProcess):
    """
    Extends QProcess with methods to easily manipulate the server process.

    Also logs everything that is written to the process' stdout/stderr.
    """
    def __init__(self, parent):
        super().__init__(parent)
        self.started.connect(self._on_process_started)
        self.error.connect(self._on_process_error)
        self.finished.connect(self._on_process_finished)
        self.readyReadStandardOutput.connect(self._on_process_stdout_ready)
        self.readyReadStandardError.connect(self._on_process_stderr_ready)
        self.running = False
        self._srv_logger = logging.getLogger('pyqode.server')
        self._test_not_deleted = False

    def _on_process_started(self):
        """ Logs process started """
        _logger().debug('server process started')
        self.running = True

    def _on_process_error(self, error):
        """ Logs process error """
        if error not in PROCESS_ERROR_STRING:
            error = -1
        try:
            self._test_not_deleted
        except AttributeError:
            pass
        else:
            if self.running:
                _logger().error('server process error %s: %s', error,
                                PROCESS_ERROR_STRING[error])

    def _on_process_finished(self, exit_code):
        """ Logs process exit status """
        _logger().info('server process finished with exit code %d',
                       exit_code)
        try:
            self.running = False
        except AttributeError:
            pass

    def _on_process_stdout_ready(self):
        """ Logs process output """
        try:
            o = self.readAllStandardOutput()
            try:
                output = bytes(o).decode('utf-8')
            except TypeError:
                output = bytes(o.data()).decode('utf-8')
            output = output[:output.rfind('\n')]
            for line in output.splitlines():
                self._srv_logger.debug(line)
        except RuntimeError:
            pass

    def _on_process_stderr_ready(self):
        """ Logs process output (stderr) """
        if not self:
            return
        o = self.readAllStandardError()
        try:
            output = bytes(o).decode('utf-8')
        except TypeError:
            output = bytes(o.data()).decode('utf-8')
        output = output[:output.rfind('\n')]
        for line in output.splitlines():
            self._srv_logger.error(line)

    def terminate(self):
        """ Terminate the process """
        self.running = False
        super(_ServerProcess, self).terminate()
