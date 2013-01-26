#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# PCEF - PySide Code Editing framework
# Copyright 2013, Colin Duquesnoy <colin.duquesnoy@gmail.com>
#
# This software is released under the LGPLv3 license.
# You should have received a copy of the GNU Lesser General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
""" Contains the right margin mode
"""
from PySide.QtGui import QPainter
from PySide.QtGui import QPen
from pcef.base import Mode


class RightMarginMode(Mode):
    """
    Display the right margin
    """
    #: Mode identifier
    IDENTIFIER = "RightMargin"

    def __init__(self):
        Mode.__init__(self, self.IDENTIFIER, "Draw the right margin on the "
                                             "document")
        #: Defines the margin position
        self.marginPos = 80

    def install(self, editor):
        """
        :type editor: pcef.editors.QGenericEditor
        """
        super(RightMarginMode, self).install(editor)
        editor.textEdit.postPainting.connect(self.__paintMargin)

    def updateStyling(self):
        """ Updates the margin pen color """
        self.pen = QPen(self.currentStyle.marginColor)

    def __paintMargin(self, event):
        """ Paints the right margin as postPainting step. """
        if self.enabled:
            rect = event.rect()
            fm = self.editor.textEdit.fm
            pos = self.marginPos
            offset = self.editor.textEdit.contentOffset().x() +\
                     self.editor.textEdit.document().documentMargin()
            x80 = round(fm.averageCharWidth() * pos) + offset
            p = QPainter(self.editor.textEdit.viewport())
            p.setPen(self.pen)
            p.drawLine(x80, rect.top(), x80, rect.bottom())