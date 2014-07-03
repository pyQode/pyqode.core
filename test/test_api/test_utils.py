from pyqode.core.api import utils
from pyqode.core.qt import QtWidgets, QtGui
from pyqode.core.qt.QtTest import QTest
import time
from pyqode.core.api import CodeEdit


def test_memoized():
    @utils.memoized
    def memoized(*args):
        print(args)
        return 2

    class Memoized:
        @utils.memoized
        def memoized(*args):
            print(args)
            return 2

    assert memoized(1) == 2
    assert memoized("foo") == 2
    assert memoized("foo") == 2
    assert memoized(1, [1, 2, 3]) == 2
    assert Memoized().memoized(None) == 2


def test_drift_color():
    assert utils.drift_color(QtGui.QColor("#FFFFFF")).name() == \
           QtGui.QColor("#e8e8e8").name()

    assert utils.drift_color(QtGui.QColor("#202020")).name() == \
           QtGui.QColor("#262626").name()

    assert utils.drift_color(QtGui.QColor("#000000")).name() == \
           QtGui.QColor("#202020").name()


def test_text_style():
    s = utils.TextStyle()
    s = utils.TextStyle('#808000 bold italic underlined')
    assert s.color.name() == '#808000'
    assert s.bold
    assert s.italic
    assert s.underlined
    s = utils.TextStyle('#808000 nbold nitalic nunderlined')
    assert not s.bold
    assert not s.italic
    assert not s.underlined


editor = None


def job():
    print('run')
    time.sleep(0.1)


def test_delay_job_runner():
    print('test delay job runner')
    global editor
    editor = CodeEdit()
    job_runner = utils.DelayJobRunner()
    job_runner.request_job(job)
    QTest.qWait(1000)
    job_runner.request_job(job)
    QTest.qWait(1000)
