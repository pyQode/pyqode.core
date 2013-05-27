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
"""
Contains the python code folder mode.
"""
from pcef.modes.python import analyser
from pcef.core import Mode
from pcef.panels.folding import FoldPanel


def get_markers(root_node):
    markers = []
    for c in root_node.children:
        markers.append((c.start, c.end))
        markers += get_markers(c)
    return markers

class PyFolderMode(Mode):
    """
    Mode that manage the fold panel using the analyze module
    """
    NAME = "Python folder mode"
    DESCRIPTION = "Manage the fold panel for a python source code"

    def __init__(self):
        Mode.__init__(self, self.NAME, self.DESCRIPTION)
        self.__nbLines = 0

    def _onStateChanged(self, state):
        """
        Called when the mode is activated/deactivated
        """
        if state:
            self.editor.codeEdit.blockCountChanged.connect(
                self.__onTextChanged)
            self.editor.codeEdit.newTextSet.connect(self.__onTextChanged)
        else:
            self.editor.codeEdit.blockCountChanged.disconnect(
                self.__onTextChanged)
            self.editor.codeEdit.newTextSet.disconnect(self.__onTextChanged)

    def __onTextChanged(self):
        """
        Update the fold panel markers if the number of lines changed using
        the PyDocAnalyser
        :return:
        """
        try:
            foldPanel = self.editor.foldPanel
        except KeyError:
            return
        assert isinstance(foldPanel, FoldPanel)
        foldPanel.clearIndicators()
        root_node = analyser.parse(self.editor.codeEdit.toPlainText())
        for start, end in get_markers(root_node):
            foldPanel.addIndicator(start, end)

