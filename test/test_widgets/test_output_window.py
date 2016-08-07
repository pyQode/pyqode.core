import os
from pyqode.core.widgets import output_window
from pyqode.qt import QtTest, QtCore


DIRECTORY = os.path.dirname(__file__)
with open(os.path.join(DIRECTORY, 'raw_output.txt')) as f:
    RAW_OUTPUT = f.read()
with open(os.path.join(DIRECTORY, 'parsed_output.txt')) as f:
    PARSED_OUTPUT = f.read()


def test_parser():
    # functional test
    parser = output_window.AnsiEscapeCodeParser()
    operations = parser.parse_text(output_window.FormattedText(RAW_OUTPUT))
    assert len(operations) == 772

    # check if bold+underlined is correctly set
    op = operations[550]
    assert op.command == 'draw'
    assert isinstance(op.data, output_window.FormattedText)
    from pyqode.qt import QtGui
    assert isinstance(op.data.fmt, QtGui.QTextCharFormat)
    assert op.data.txt == 'bold+underl'
    assert op.data.fmt.fontUnderline() is True
    assert op.data.fmt.font().weight() == QtGui.QFont.Bold

    # check if reset format has been done
    op = operations[551]
    assert op.command == 'draw'
    assert isinstance(op.data, output_window.FormattedText)
    assert isinstance(op.data.fmt, QtGui.QTextCharFormat)
    assert op.data.txt == '|normal|'
    assert op.data.fmt.fontUnderline() is False
    assert op.data.fmt.font().weight() != QtGui.QFont.Bold


def test_output_window_results():
    # functional test
    w = output_window.OutputWindow()
    w._formatter.append_message(RAW_OUTPUT)
    assert w.blockCount() == 173
    assert w.toPlainText() == PARSED_OUTPUT


def test_output_window():
    w = output_window.OutputWindow()
    w.start_process('bash', arguments=['-l', '-i'], env={'TERM': 'xterm'})
    w.show()
    QtTest.QTest.qWait(1000)
    w.stop_process()
    QtTest.QTest.qWait(1000)
    assert not w.is_running
    assert w.process is not None


def test_immediate_input_handler():
    w = output_window.OutputWindow(input_handler=output_window.ImmediateInputHandler())
    w.start_process('bash', arguments=['-l', '-i'], env={'TERM': 'xterm'}, print_command=False)
    w.show()
    QtTest.QTest.qWait(1000)
    assert w.blockCount() == 1
    QtTest.QTest.keyPress(w, QtCore.Qt.Key_L)
    QtTest.QTest.keyPress(w, QtCore.Qt.Key_S)
    assert w.blockCount() == 1
    QtTest.QTest.keyPress(w, QtCore.Qt.Key_Return)
    QtTest.QTest.qWait(1000)
    assert w.blockCount() >= 2
