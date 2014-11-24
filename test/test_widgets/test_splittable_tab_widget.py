from pyqode.core.widgets import SplittableTabWidget, SplittableCodeEditTabWidget, GenericCodeEdit, InteractiveConsole
from pyqode.qt import QtCore

from pyqode.core.backend import server
from pyqode.qt.QtTest import QTest


def test_splittable_tab_widget():
    tw = SplittableTabWidget()
    tw.show()
    w = GenericCodeEdit()
    tw.add_tab(w)
    tw.add_tab(InteractiveConsole())
    tw.split(w, QtCore.Qt.Vertical)
    w.close()
    tw.close()
    del tw


def test_splittable_codedit_tab_widget():
    tw = SplittableCodeEditTabWidget()
    tw.show()
    nd = tw.create_new_document()
    QTest.keyPress(nd, 'a')
    w_file = tw.open_document(__file__)
    QTest.qWait(1000)
    other = tw.open_document(server.__file__)
    assert tw.current_widget() == other
    assert other != w_file
    assert tw.open_document(__file__) == w_file
    QTest.qWait(1000)
    assert tw.count() == 3
    tw.rename_document(__file__, __file__ + '.old')
    QTest.qWait(1000)
    tw.close_document(__file__ + '.old')
    QTest.qWait(1000)
    assert tw.count() == 2
    tw.close_document(server.__file__)
    QTest.qWait(1000)
    assert tw.count() == 1
    tw.close_all()
    QTest.qWait(1000)
    assert tw.count() == 0
    tw.close()
    del tw
