#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import logging
logging.basicConfig(level=logging.DEBUG)
from PyQt4 import QtCore, QtGui
from pyqode.core import modes
from pyqode.core import panels
from pyqode.core.editor import Panel
from ui.simple_editor_ui import Ui_MainWindow


class SimpleEditorWindow(QtGui.QMainWindow, Ui_MainWindow):
    def __init__(self):
        QtGui.QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)
        # configure editor widget
        self.editor.install_panel(panels.LineNumberPanel(), Panel.Position.LEFT)
        self.editor.install_panel(panels.SearchAndReplacePanel(),
                                 Panel.Position.BOTTOM)

        self.editor.install_mode(modes.AutoCompleteMode())
        self.editor.install_mode(modes.CaseConverterMode())
        self.editor.install_mode(modes.FileWatcherMode())
        self.editor.install_mode(modes.CaretLineHighlighterMode())
        self.editor.install_mode(modes.RightMarginMode())
        self.editor.install_mode(modes.PygmentsSyntaxHighlighter(
            self.editor.document()))
        self.editor.install_mode(modes.ZoomMode())
        self.editor.install_mode(modes.CodeCompletionMode())
        self.editor.install_mode(modes.AutoIndentMode())
        self.editor.install_mode(modes.IndenterMode())
        self.editor.install_mode(modes.SymbolMatcherMode())

        # start pyqode server
        self.editor.start_server('../server.py')

        # connect to editor signals
        self.editor.dirty_changed.connect(self.actionSave.setEnabled)
        self.actionSave.triggered.connect(self.editor.save_to_file)
        self.actionOpen.setIcon(
            QtGui.QIcon.fromTheme("document-open", QtGui.QIcon(
                ":/example_icons/rc/folder.png")))
        self.actionSave.setIcon(
            QtGui.QIcon.fromTheme("document-save", QtGui.QIcon(
                ":/example_icons/rc/document-save.png")))
        # edit menu
        mnu = QtGui.QMenu("Edit", self.menubar)
        mnu.addActions(self.editor.actions())
        self.menubar.addMenu(mnu)
        self.setupModesMenu()
        self.setupPanelsMenu()
        self.setupStylesMenu()
        try:
            self.editor.open_file(__file__, detect_encoding=True)
        except (OSError, IOError):
            pass
        except AttributeError:
            pass

    def setupStylesMenu(self):
        group = QtGui.QActionGroup(self)
        currentStyle = self.editor.style.value("pygmentsStyle")
        group.triggered.connect(self.onStyleTriggered)
        for style in sorted(modes.PYGMENTS_STYLES):
            a = QtGui.QAction(self.menuStyles)
            a.setText(style)
            a.setCheckable(True)
            if style == currentStyle:
                a.setChecked(True)
            group.addAction(a)
            self.menuStyles.addAction(a)

    def setupModesMenu(self):
        # Add modes to the modes menu
        for k, v in sorted(self.editor.get_modes().items()):
            a = QtGui.QAction(self.menuModes)
            a.setText(k)
            a.setCheckable(True)
            a.setChecked(True)
            a.changed.connect(self.onModeCheckStateChanged)
            a.mode = v
            self.menuModes.addAction(a)

    def setupPanelsMenu(self):
        for zones, panel_dic in sorted(self.editor.get_panels().items()):
            for k, v in panel_dic.items():
                a = QtGui.QAction(self.menuModes)
                a.setText(k)
                a.setCheckable(True)
                a.setChecked(True)
                a.changed.connect(self.onPanelCheckStateChanged)
                a.panel = v
                self.menuPanels.addAction(a)

    @QtCore.pyqtSlot(QtGui.QAction)
    def onStyleTriggered(self, action):
        self.editor.style.set_value("pygmentsStyle", action.text())

    @QtCore.pyqtSlot()
    def on_actionOpen_triggered(self):
        filePath = QtGui.QFileDialog.getOpenFileName(
            self, "Choose a file", os.path.expanduser("~"))
        if filePath:
            self.editor.open_file(filePath, detect_encoding=True)

    def onPanelCheckStateChanged(self):
        action = self.sender()
        action.panel.enabled = action.isChecked()

    def onModeCheckStateChanged(self):
        action = self.sender()
        action.mode.enabled = action.isChecked()


def main():
    try:
        import faulthandler
        faulthandler.enable()
    except ImportError:
        pass
    app = QtGui.QApplication(sys.argv)
    win = SimpleEditorWindow()
    win.show()
    print(win.editor.settings.dumps())
    print(win.editor.style.dumps())
    print(app)
    app.exec_()
    # cleanup
    win.editor.stop_server()  # ensure the server is properly closed.
    del win
    del app

if __name__ == "__main__":
    main()
