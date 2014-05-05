# -*- coding: utf-8 -*-
"""
A series of simple integration test, we check that a simple pyqode application
is running as expected, that the client server architecture works
as intended
"""
import os
import sys
import logging
from PyQt4.QtTest import QTest
from PyQt4 import QtGui
from pyqode.core import frontend
from pyqode.core.frontend import modes, panels
from .helpers import cwd_at


# -----------------
# Simple application test
# -----------------
@cwd_at('test')
def test_app():
    """
    Test a simple but complete app
    """
    # def _leave():
    #     """
    #     Leave test_app after a certain amount of time.
    #     """
    #     app = QtGui.QApplication.instance()
    #     app.quit()
    app = QtGui.QApplication.instance()
    editor = frontend.CodeEdit()
    frontend.start_server(editor, os.path.join(os.getcwd(), 'server.py'))

    # install the same modes/panels as in the simple_editor example
    # add panels
    frontend.install_panel(editor, panels.LineNumberPanel())
    frontend.install_panel(editor, panels.SearchAndReplacePanel(),
                           panels.SearchAndReplacePanel.Position.BOTTOM)
    # add modes
    frontend.install_mode(editor, modes.AutoCompleteMode())
    frontend.install_mode(editor, modes.CaseConverterMode())
    frontend.install_mode(editor, modes.FileWatcherMode())
    frontend.install_mode(editor, modes.CaretLineHighlighterMode())
    frontend.install_mode(editor, modes.RightMarginMode())
    frontend.install_mode(editor, modes.PygmentsSyntaxHighlighter(
        editor.document()))
    frontend.install_mode(editor, modes.ZoomMode())
    frontend.install_mode(editor, modes.CodeCompletionMode())
    frontend.install_mode(editor, modes.AutoIndentMode())
    frontend.install_mode(editor, modes.IndenterMode())
    frontend.install_mode(editor, modes.SymbolMatcherMode())

    frontend.open_file(editor, __file__)
    # editor.show()
    # QtCore.QTimer.singleShot(2000, _leave)
    QTest.qWait(2000)
    frontend.stop_server(editor)
    del editor
