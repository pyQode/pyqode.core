# -*- coding: utf-8 -*-
"""
This module contains interactive widgets:
    - interactive console: a text edit made to run subprocesses interactively
"""
import logging
from pyqode.qt.QtCore import Qt, Signal, pyqtProperty as Property, QProcess
from PyQt5.QtWidgets import QTextEdit
from PyQt5.QtGui import QColor, QTextCursor
from pyqode.core.frontend.client import PROCESS_ERROR_STRING
# pylint: disable=too-many-instance-attributes, missing-docstring


def _logger():
    return logging.getLogger(__name__)


class InteractiveConsole(QTextEdit):
    """
    An interactive console is a QTextEdit specialised to run a process
    interactively

    The user will see the process outputs and will be able to
    interact with the process by typing some text, this text will be forwarded
    to the process stdin.

    You can customize the colors using the following attributes:
        - stdout_color: color of the process' stdout
        - stdin_color: color of the user inputs. Green by default
        - app_msg_color: color for custom application message (
                         process started, process finished)
        - stderr_color: color of the process' stderr

    """
    #: Signal emitted when the process has finished.
    process_finished = Signal(int)

    def __init__(self, parent=None):
        QTextEdit.__init__(self, parent)
        self._stdout_col = QColor("#404040")
        self._app_msg_col = QColor("#4040FF")
        self._stdin_col = QColor("#22AA22")
        self._stderr_col = QColor("#FF0000")
        self._process = None
        self._args = None
        self._usr_buffer = ""
        self._clear_on_start = True
        self.process = QProcess()
        self._merge_outputs = False
        self.process.finished.connect(self._write_finished)
        self.process.error.connect(self._write_error)
        self.process.readyReadStandardError.connect(self._on_stderr)
        self.process.readyReadStandardOutput.connect(self._on_stdout)
        self._running = False
        self._writer = self.write
        self._user_stop = False

    def set_writer(self, writer):
        """
        Changes the writer function to handle writing to the text edit.

        A writer function must have the following prototype:

        .. code-block:: python

            def write(text_edit, text, color)
        """
        if self._writer != writer and self._writer:
            self._writer = None
        if writer:
            self._writer = writer

    def _on_stdout(self):
        txt = bytes(self.process.readAllStandardOutput()).decode('utf-8')
        logging.debug('stdout ready: %s', txt)
        self._writer(self, txt, self.stdout_color)

    def _on_stderr(self):
        txt = bytes(self.process.readAllStandardError()).decode('utf-8')
        logging.debug('stderr ready: %s', txt)
        self._writer(self, txt, self.stderr_color)

    def _get_background_col(self):
        pal = self.palette()
        return pal.color(pal.Base)

    def _set_background_color(self, color):
        pal = self.palette()
        pal.setColor(pal.Base, color)
        pal.setColor(pal.Text, self.stdout_color)
        self.setPalette(pal)

    #: The console background color. Default is white.
    background_color = Property(
        QColor, _get_background_col, _set_background_color,
        "The console background color")

    def _get_stdout_col(self):
        return self._stdout_col

    def _set_stdout_col(self, color):
        self._stdout_col = color
        pal = self.palette()
        pal.setColor(pal.Text, self.stdout_color)
        self.setPalette(pal)

    #: Color of the process output. Default is black.
    stdout_color = Property(
        QColor, _get_stdout_col, _set_stdout_col,
        doc="The color of the process output (stdout)")

    def _get_err_col(self):
        return self._stderr_col

    def _set_err_col(self, color):
        self._stderr_col = color

    #: Color for stderr output if
    # :attr:`pyqode.widgets.QInteractiveConsole.mergeStderrWithStdout`is False.
    stderr_color = Property(
        QColor, _get_err_col, _set_err_col,
        doc="The color of the error messages (stderr)")

    def _get_stdin_col(self):
        return self._stdin_col

    def _set_stdin_col(self, color):
        self._stdin_col = color

    #: Color for user inputs. Default is green.
    stdin_color = Property(
        QColor, _get_stdin_col, _set_stdin_col,
        doc="The color of the user inputs (stdin)")

    def _get_app_message_color(self):
        return self._app_msg_col

    def _set_app_message_color(self, color):
        self._app_msg_col = color

    #: Color of the application messages (e.g.: 'Process started',
    #: 'Process finished with status %d')
    app_msg_color = Property(
        QColor, _get_app_message_color, _set_app_message_color,
        doc="Color of the application messages ('Process started', "
        "'Process finished with status %d')")

    def _get_clear_on_start(self):
        return self._clear_on_start

    def _set_clear_on_start(self, value):
        self._clear_on_start = value

    clear_on_start = Property(bool, _get_clear_on_start, _set_clear_on_start,
                              doc='Clears output when the process starts')

    def _get_merge_outputs(self):
        """
        Merge stderr with stdout. Default is False.

        If set to true, stderr and stdin won't have distinctive colors, i.e.
        stderr output will display with the same color as stdout.

        """
        return self._merge_outputs

    def _set_merge_outputs(self, value):
        self._merge_outputs = value
        if value:
            self.process.setProcessChannelMode(QProcess.MergedChannels)
        else:
            self.process.setProcessChannelMode(QProcess.SeparateChannels)

    merge_outputs = Property(bool, _get_merge_outputs, _set_merge_outputs,
                             doc='Merges stdout and stderr. Default is False')

    def closeEvent(self, *args, **kwargs):
        # pylint: disable=invalid-name, unused-argument
        if self.process.state() == QProcess.Running:
            self.process.terminate()

    def start_process(self, process, args=None, cwd=None):
        """
        Starts a process interactively.

        :param process: Process to run
        :type process: str

        :param args: List of arguments (list of str)
        :type args: list

        :param cwd: Working directory
        :type cwd: str
        """
        if args is None:
            args = []
        if not self._running:
            if cwd:
                self.process.setWorkingDirectory(cwd)
            self._running = True
            self._process = process
            self._args = args
            if self._clear_on_start:
                self.clear()
            self._user_stop = False
            self.process.start(process, args)
            self._write_started()
        else:
            _logger().warning('a process is already running')

    def stop_process(self):
        _logger().debug('killing process')
        self.process.kill()
        self._user_stop = True

    def keyPressEvent(self, event):
        # pylint: disable=invalid-name
        if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            # send the user input to the child process
            self._usr_buffer += "\n"
            self.process.write(bytes(self._usr_buffer, "utf-8"))
            self._usr_buffer = ""
        else:
            if event.key() != Qt.Key_Backspace:
                txt = event.text()
                self._usr_buffer += txt
                self.setTextColor(self._stdin_col)
            else:
                self._usr_buffer = self._usr_buffer[
                    0:len(self._usr_buffer) - 1]
        # text is inserted here, the text color must be defined before this
        # line
        QTextEdit.keyPressEvent(self, event)

    def _write_finished(self, exit_code, exit_status):
        self._writer(self, "\nProcess finished with exit code %d" % exit_code,
                     self._app_msg_col)
        self._running = False
        _logger().debug('process finished (exit_code=%r, exit_status=%r)',
                        exit_code, exit_status)
        self.process_finished.emit(exit_code)

    def _write_started(self):
        self._writer(self, "{0} {1}\n".format(
            self._process, " ".join(self._args)), self._app_msg_col)
        self._running = True
        _logger().debug('process started')

    def _write_error(self, error):
        if self._user_stop:
            self._writer(self, '\nProcess stopped by the user',
                         self.app_msg_color)
            self._user_stop = False
        else:
            self._writer(self, "Failed to start {0} {1}\n".format(
                self._process, " ".join(self._args)), self.app_msg_color)
            err = PROCESS_ERROR_STRING[error]
            self._writer(self, "Error: %s" % err, self.stderr_color)
            _logger().debug('process error: %s', err)
        self._running = False

    @staticmethod
    def write(text_edit, text, color):
        """
        Default write function. Move the cursor to the end and insert text with
        the specified color.

        :param text_edit: QInteractiveConsole instance
        :type text_edit: pyqode.widgets.QInteractiveConsole

        :param text: Text to write
        :type text: str

        :param color: Desired text color
        :type color: QColor
        """
        text_edit.moveCursor(QTextCursor.End)
        text_edit.setTextColor(color)
        text_edit.insertPlainText(text)
        text_edit.moveCursor(QTextCursor.End)
