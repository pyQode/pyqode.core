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
"""An easy to use and easy to customise full featured code editor for PySide
applications.

This module contains helper functions for the end user.
"""
import sys
import logging
from version import __version__ as pcef_version

# create logger with 'spam_application'
module_logger = logging.getLogger(__name__)
module_logger.setLevel(logging.DEBUG)
# create console handler with a higher log level
ch = logging.StreamHandler("")
ch.name = "pcef"
ch.setLevel(logging.ERROR)
# create formatter and add it to the handlers
formatter = logging.Formatter('%(levelname)s <%(name)s>: %(message)s')
ch.setFormatter(formatter)
# add the handlers to the logger
module_logger.info("#" * 80)
module_logger.info("PCEF v{0}".format(pcef_version))
module_logger.addHandler(ch)


def openFileInEditor(editor, filename, encoding=sys.getfilesystemencoding(),
                     replaceTabsBySpaces=True):
    """
    Open a file in an editor

    :param editor: Editor instance where the file content will be displayed

    :param filename: Filename of the file to open

    :param encoding: Encoding to use to load the file

    :param replaceTabsBySpaces: True to replace tabs by spaces
    """
    with open(filename, 'r') as f:
        content = unicode(f.read().decode(encoding))
    if replaceTabsBySpaces:
        content = content.replace("\t", " " * editor.TAB_SIZE)
    editor.codeEdit.tagFilename = filename
    editor.codeEdit.tagEncoding = encoding

    editor.syntaxHighlightingMode.setLexerFromFilename(filename)
    editor.codeEdit.setPlainText(content)
    editor.ui.codeEdit.dirty = False
    module_logger.info("File opened: {0}".format(filename))


def saveFileFromEditor(editor, filename=None,
                       encoding=sys.getfilesystemencoding()):
    """
    Save the editor content to a file

    :param editor: Editor instance

    :param filename: The filename to save. If none the editor filename attribute is used.

    :param encoding: The save encoding
    """
    if filename is None:
        filename = editor.codeEdit.tagFilename
    if encoding is None:
        encoding = editor.codeEdit.tagEncoding
    content = unicode(editor.codeEdit.toPlainText()).encode(encoding)
    with open(filename, "w") as f:
        f.write(content)
    editor.codeEdit.dirty = False
    editor.codeEdit.tagFilename = filename
    editor.codeEdit.tagEncoding = encoding
    editor.codeEdit.textSaved.emit(filename)
    module_logger.info("File saved: {0}".format(filename))
