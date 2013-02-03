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
import logging
from version import __version__ as pcef_version

# create logger with 'spam_application'
module_logger = logging.getLogger(__name__)
module_logger.setLevel(logging.DEBUG)
# create file handler which logs even debug messages
fh = logging.FileHandler('pcef.log')
fh.setLevel(logging.DEBUG)
# create console handler with a higher log level
ch = logging.StreamHandler()
ch.setLevel(logging.ERROR)
# create formatter and add it to the handlers
formatter = logging.Formatter('%(levelname)s <%(name)s>: %(message)s')
fh.setFormatter(formatter)
ch.setFormatter(formatter)
# add the handlers to the logger
module_logger.addHandler(fh)
module_logger.info("#" * 80)
module_logger.info("PCEF v{0}".format(pcef_version))
module_logger.addHandler(ch)


def openFileInEditor(editor, filename, encoding='utf8',
                     replaceTabsBySpaces=True):
    """
    Open a file in an editor
    :param editor: Editor instance where the file content will be displayed
    :param filename: Filename of the file to open
    :param encoding: Encoding to use to load the file
    """
    with open(filename, 'r') as f:
        content = unicode(f.read().decode(encoding))
    if replaceTabsBySpaces:
        content = content.replace("\t", " " * editor.TAB_SIZE)
    editor.textEdit.filename = filename
    editor.textEdit.encoding = encoding
    editor.syntaxHighlightingMode.setLexerFromFilename(filename)
    editor.textEdit.setPlainText(content)
    editor.ui.textEdit.dirty = False
    module_logger.info("File opened: {0}".format(filename))


def saveFileFromEditor(editor, filename=None, encoding=None):
    """
    Save the editor content to a file
    :param editor: Editor instance
    :param filename: The filename to save. If none the editor filename attribute is used.
    :param encoding: The save encoding
    """
    if filename is None:
        filename = editor.textEdit.filename
    if encoding is None:
        encoding = editor.textEdit.encoding
    content = unicode(editor.textEdit.toPlainText()).encode(encoding)
    with open(filename, "w") as f:
        f.write(content)
    editor.textEdit.dirty = False
    editor.textEdit.filename = filename
    editor.textEdit.encoding = encoding
    module_logger.info("File saved: {0}".format(filename))
