from PyQt4 import QtGui
from PyQt4.QtTest import QTest
import time
from pyqode.core import frontend
from pyqode.core.frontend import utils


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
flag = False


def add_deco():
    global flag
    print('run')
    flag = True
    time.sleep(0.1)


def test_job_runner():
    global editor, flag
    flag = False
    editor = frontend.CodeEdit()
    job_runner = utils.JobRunner(editor)
    job_runner.start_job(add_deco, force=True)
    job_runner.start_job(add_deco, force=False)
    assert job_runner.job_running
    QTest.qWait(2000)
    assert flag is True
    for i in range(10):
        job_runner.start_job(add_deco, force=False)
    QTest.qWait(2000)


def test_delay_job_runner():
    global editor, flag
    flag = False
    editor = frontend.CodeEdit()
    job_runner = utils.DelayJobRunner(editor)
    job_runner.request_job(add_deco, async=False)
    QTest.qWait(1000)
    job_runner.request_job(add_deco, async=True)
    QTest.qWait(1000)
