#!/usr/bin/env python2
# -*- coding: utf-8 -*-
#
# PCEF
# Copyright 2013, Colin Duquesnoy <colin.duquesnoy@gmail.com>
#
# This software is released under the LGPLv3 license.
# You should have received a copy of the GNU Lesser General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
"""
This package contains python specific modes, panels and editors.
"""
from pcef.python import panels
from pcef.python import modes

from pcef.core.editor import QCodeEdit
from pcef.core.panels import LineNumberPanel
from pcef.core.modes import CaretLineHighlighterMode
from pcef.core.modes import RightMarginMode
from pcef.core.modes import ZoomMode
from pcef.python.modes import PyHighlighterMode
from pcef.python.modes import PyAutoIndentMode
from pcef.constants import PanelPosition

from pcef.qt import QtCore
from pcef import constants


class QPythonCodeEdit(QCodeEdit):
    """
    Extends QCodeEdit with a hardcoded set of modes and panels specifics to
    a python code editor widget

    **Panels:**
        * line number panel
        * search and replace panel

    **Modes:**
        * document word completion
        * generic syntax highlighter (pygments)
    """
    DARK_STYLE = 0
    LIGHT_STYLE = 1

    def __init__(self, parent=None):
        QCodeEdit.__init__(self, parent)
        self.setLineWrapMode(self.NoWrap)
        self.setWindowTitle("PCEF - Generic Editor")
        self.installPanel(LineNumberPanel(), PanelPosition.LEFT)
        self.installMode(CaretLineHighlighterMode())
        self.installMode(RightMarginMode())
        self.installMode(PyHighlighterMode(self.document()))
        self.installMode(ZoomMode())
        self.installMode(PyAutoIndentMode())

    @QtCore.Slot()
    def useDarkStyle(self, use=True):
        if not use:
            return
        for k, v in constants.DEFAULT_DARK_STYLES.iteritems():
            self.style.setValue(k, v, "Python")
        self.style.setValue("background", "#252525")
        self.style.setValue("foreground", "#A9B7C6")
        self.style.setValue("caretLineBackground", "#2d2d2d")
        self.style.setValue("selectionBackground",
                            '#78879b')
        self.style.setValue("selectionForeground",
                            "white")
        self.style.setValue("panelBackground",
                            '#302F2F')
        self.style.setValue("panelForeground",
                            '#808080')
        self.style.setValue("whiteSpaceForeground",
                            '#404040')
        self.pyHighlighter.rehighlight()

    @QtCore.Slot()
    def useLightStyle(self, use=True):
        if not use:
            return
        for k, v in constants.DEFAULT_STYLES.iteritems():
            self.style.setValue(k, v, "Python")
        self.style.setValue("background", "white")
        self.style.setValue("foreground", "black")
        self.style.setValue("caretLineBackground", "#E4EDF8")
        self.style.setValue("selectionBackground",
                            constants.SELECTION_BACKGROUND)
        self.style.setValue("selectionForeground",
                            constants.SELECTION_FOREGROUND)
        self.style.setValue("panelBackground",
                            constants.LINE_NBR_BACKGROUND)
        self.style.setValue("panelForeground",
                            constants.LINE_NBR_FOREGROUND)
        self.style.setValue("whiteSpaceForeground",
                            constants.EDITOR_WS_FOREGROUND)
        self.pyHighlighter.rehighlight()

