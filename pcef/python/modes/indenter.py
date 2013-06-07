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
""" Contains smart indent modes """
from pcef.qt.QtGui import QTextCursor
from pcef.core.modes.indenter import AutoIndentMode


class PyAutoIndentMode(AutoIndentMode):
    """ A basic auto indent mode that provides a basic auto indentation based on the previous
    line indentation.

    This mode can be extended by overriding the _getIndent method.
    """
    #: Mode identifier
    IDENTIFIER = "pyAutoIndent"
    #: Mode description
    _DESCRIPTION = """ This mode provides python specific auto indentation. """

    def __init__(self):
        super(PyAutoIndentMode, self).__init__()

    def _getIndent(self, tc):
        """
        Return the indentation text (a series of spaces, tabs)

        The indentation level is based on the indentation level of the previous
        line

        :param tc: QTextCursor
        """
        pos = tc.position()
        if pos != 0:
            indent = AutoIndentMode._getIndent(self, tc)
            tc.movePosition(QTextCursor.StartOfLine, QTextCursor.MoveAnchor, -1)
            tc.movePosition(QTextCursor.WordLeft)
            tc.select(QTextCursor.WordUnderCursor)
            last_word = tc.selectedText().strip()
            tc.select(QTextCursor.LineUnderCursor)
            line = tc.selectedText().strip()
            tc.movePosition(QTextCursor.Left, QTextCursor.KeepAnchor, 1)
            last_char = tc.selectedText().strip()
            if line.endswith(":"):
                indent += 4 * " "
            elif last_word in ["return", "pass"] or \
                    (last_char == "" and last_word == ""):
                indent = indent[4:]
            tc.setPosition(pos)
            return indent
        return ""
