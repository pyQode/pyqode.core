#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# PCEF - Python/Qt Code Editing Framework
# Copyright 2013, Colin Duquesnoy <colin.duquesnoy@gmail.com>
#
# This software is released under the LGPLv3 license.
# You should have received a copy of the GNU Lesser General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
""" Contains the right margin mode
"""
from PySide.QtGui import QPainter, QFontMetricsF, QFont, QFontMetrics
from PySide.QtGui import QPen
from pcef.core import Mode


class RightMarginMode(Mode):
    """
    Display the right margin
    """
    #: Mode identifier
    IDENTIFIER = "Right margin"

    def __init__(self):
        Mode.__init__(self, self.IDENTIFIER, "Draw the right margin on the "
                                             "document")
        #: Defines the margin position. 80 is the default
        self.marginPos = 80

    def _onStyleChanged(self):
        """ Updates the margin pen color """
        self.pen = QPen(self.currentStyle.marginColor)

    def _onStateChanged(self, state):
        if state is True:
            self.editor.codeEdit.postPainting.connect(self.__paintMargin)
        else:
            self.editor.codeEdit.postPainting.disconnect(self.__paintMargin)

    def __paintMargin(self, event):
        """ Paints the right margin as postPainting step. """
        rect = event.rect()
        font = self.editor.codeEdit.currentCharFormat().font()
        fm = QFontMetricsF(font)
        pos = self.marginPos
        offset = self.editor.codeEdit.contentOffset().x() + \
                 self.editor.codeEdit.document().documentMargin()
        x80 = round(fm.width(' ') * pos) + offset
        p = QPainter(self.editor.codeEdit.viewport())
        p.setPen(self.pen)
        p.drawLine(x80, rect.top(), x80, rect.bottom())