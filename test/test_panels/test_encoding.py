import os
from pyqode.qt.QtTest import QTest
from pyqode.core import panels


PATH = pth = os.path.join(os.getcwd(), 'test', 'files', 'big5hkscs.txt')


def get_panel(editor):
    return editor.panels.get(panels.EncodingPanel)


def test_enabled(editor):
    editor.panels.append(panels.EncodingPanel(),
                         panels.EncodingPanel.Position.TOP)
    panel = get_panel(editor)
    assert panel.enabled
    panel.enabled = False
    panel.enabled = True


def test_reload(editor):
    editor.panels.append(panels.EncodingPanel(),
                         panels.EncodingPanel.Position.TOP)
    editor.file.open(PATH, encoding='utf_8', use_cached_encoding=False)
    editor.show()
    QTest.qWait(1000)
    pnl = get_panel(editor)
    assert pnl.isVisible() is True
    assert pnl.ui.comboBoxEncodings.current_encoding == 'utf_8'
    pnl.ui.comboBoxEncodings.current_encoding = 'big5hkscs'
    assert pnl.ui.comboBoxEncodings.current_encoding == 'big5hkscs'
    pnl.ui.pushButtonRetry.clicked.emit(True)
    QTest.qWait(1000)
    assert pnl.isVisible() is False


def test_edit_anyway(editor):
    editor.panels.append(panels.EncodingPanel(),
                         panels.EncodingPanel.Position.TOP)
    editor.file.open(PATH, encoding='utf_8', use_cached_encoding=False)
    editor.show()
    QTest.qWait(1000)
    pnl = get_panel(editor)
    assert pnl.isVisible() is True
    assert pnl.ui.comboBoxEncodings.current_encoding == 'utf_8'
    pnl.ui.pushButtonEdit.clicked.emit(True)
    QTest.qWait(1000)
    assert pnl.isVisible() is False


def test_cancel(editor):
    editor.panels.append(panels.EncodingPanel(),
                         panels.EncodingPanel.Position.TOP)
    editor.file.open(PATH, encoding='utf_8', use_cached_encoding=False)
    editor.show()
    QTest.qWait(1000)
    pnl = get_panel(editor)
    assert pnl.isVisible() is True
    assert pnl.ui.comboBoxEncodings.current_encoding == 'utf_8'
    pnl.ui.pushButtonCancel.clicked.emit(True)
    QTest.qWait(1000)
    assert pnl.isVisible() is False
    assert editor.toPlainText() == ''
