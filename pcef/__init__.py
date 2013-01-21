#! /usr/bin/env python2.7
# coding: latin-1
#-------------------------------------------------------------------------------
# Copyright 2012, 
#
#  This library is free software; you can redistribute it and/or
#  modify it under the terms of the GNU Lesser General Public
#  License as published by the Free Software Foundation; either
#  version 2.1 of the License, or (at your option) any later version.
#
#  This library is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
#  Lesser General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public
#  License along with this library; if not, write to the Free Software
#  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA
#-------------------------------------------------------------------------------
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
    f = open(filename, 'r')
    content = unicode(f.read().decode(encoding))
    if replaceTabsBySpaces:
        content = content.replace("\t", " " * editor.TAB_SIZE)
    editor.textEdit.setPlainText(content)
    editor.textEdit.filename = filename
    # todo change highlighter lexer here
    editor.ui.textEdit.dirty = False
    module_logger.info("File opened: {0}".format(filename))


def saveFileFromEditor(editor, filename, encoding='utf8'):
    content = unicode(editor.textEdit.toPlainText())
    f = open(filename, "w")
    f.write(content.encode(encoding))
    f.close()
    editor.textEdit.dirty = False
    editor.filename = filename
    module_logger.info("File saved: {0}".format(filename))
