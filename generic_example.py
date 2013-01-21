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
""" PCEF generic editor demo """
import sys

from PySide.QtGui import QApplication
from PySide.QtGui import QMainWindow

from pcef import openFileInEditor
from pcef.editors import QGenericEditor
from pcef.panels.utils import QBookmarkPanel


def main():
    """ Application entry point """
    # create qt objects (app, window and our editor)
    app = QApplication(sys.argv)
    window = QMainWindow()
    editor = QGenericEditor()

    # open a file
    openFileInEditor(editor, __file__)

    # install a test panel with a fixed set of markers
    p = QBookmarkPanel()
    editor.installPanel(p, editor.PANEL_ZONE_LEFT)
    # add a fold indicator around the main
    editor.foldPanel.addFoldMarker(22, 47)

    # set the editor as the central widget
    window.setCentralWidget(editor)

    # customise window PySide Code Editors Framework pcef
    window.setWindowTitle(
        "PySide Code Editing Framework - Generic Editor Example")
    window.setMinimumSize(1024, 800)

    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
