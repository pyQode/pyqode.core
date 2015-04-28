from pyqode.core.api import utils
from pyqode.qt import QtWidgets, QtGui
from pyqode.qt.QtTest import QTest
import time
from pyqode.core.api import CodeEdit


def test_memoized():
    @utils.memoized
    def memoized(*args):
        print(args)
        return 2

    class Memoized(object):
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
           QtGui.QColor("#161616").name()


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


def test_block_helper():
    editor = CodeEdit()
    editor.file.open(__file__)
    block = editor.document().findBlockByNumber(0)
    assert block.userState() == -1
    #
    # test user state
    #
    utils.TextBlockHelper.set_state(block, 0)
    assert block.userState() == 0
    utils.TextBlockHelper.set_state(block, 26)
    assert utils.TextBlockHelper.get_state(block) == 26

    #
    # test fold level
    #
    lvl = utils.TextBlockHelper.get_fold_lvl(block)
    assert lvl == 0
    utils.TextBlockHelper.set_fold_lvl(block, 5)
    lvl = utils.TextBlockHelper.get_fold_lvl(block)
    assert lvl == 5
    utils.TextBlockHelper.set_fold_lvl(block, 1024)
    lvl = utils.TextBlockHelper.get_fold_lvl(block)
    assert lvl == 1023
    # ensure other values are intact
    assert utils.TextBlockHelper.get_state(block) == 26

    #
    # Test fold trigger
    #
    assert utils.TextBlockHelper.is_fold_trigger(block) is False
    utils.TextBlockHelper.set_fold_trigger(block, True)
    assert utils.TextBlockHelper.is_fold_trigger(block) is True
    utils.TextBlockHelper.set_fold_trigger(block, False)
    assert utils.TextBlockHelper.is_fold_trigger(block) is False
    utils.TextBlockHelper.set_fold_trigger(block, True)
    # ensure other values are intact
    assert utils.TextBlockHelper.get_fold_lvl(block) == 1023
    assert utils.TextBlockHelper.get_state(block) == 26

    #
    # Test fold trigger state
    #
    assert utils.TextBlockHelper.is_collapsed(block) is False
    utils.TextBlockHelper.set_collapsed(block, True)
    assert utils.TextBlockHelper.is_collapsed(block) is True
    utils.TextBlockHelper.set_collapsed(block, False)
    assert utils.TextBlockHelper.is_collapsed(block) is False
    # ensure other values are intact
    assert utils.TextBlockHelper.is_fold_trigger(block) is True
    assert utils.TextBlockHelper.get_fold_lvl(block) == 1023
    assert utils.TextBlockHelper.get_state(block) == 26
