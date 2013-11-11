#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#The MIT License (MIT)
#
#Copyright (c) <2013> <Colin Duquesnoy and others, see AUTHORS.txt>
#
#Permission is hereby granted, free of charge, to any person obtaining a copy
#of this software and associated documentation files (the "Software"), to deal
#in the Software without restriction, including without limitation the rights
#to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#copies of the Software, and to permit persons to whom the Software is
#furnished to do so, subject to the following conditions:
#
#The above copyright notice and this permission notice shall be included in
#all copies or substantial portions of the Software.
#
#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
#THE SOFTWARE.
#
"""
This module contains Syntax Highlighting mode and the QSyntaxHighlighter based
on pygments.

.. note: This code is taken and adapted from the IPython project.
"""
from pyqode.core import logger
from pyqode.core.mode import Mode
from pyqode.core.syntax_highlighter import SyntaxHighlighter, IndentBasedFoldDetector, CharBasedFoldDetector
from pyqode.qt import QtGui, QtCore
from pyqode.qt.QtCore import QRegExp
from pygments.formatters.html import HtmlFormatter
from pygments.lexer import Error
from pygments.lexer import RegexLexer
from pygments.lexer import Text
from pygments.lexer import _TokenType
from pygments.lexers.compiled import CLexer, CppLexer
from pygments.lexers.dotnet import CSharpLexer
from pygments.lexers import get_lexer_for_filename, get_lexer_for_mimetype

try:
    from pygments.lexers.agile import PythonLexer
    from pygments.lexers.text import BashLexer
    from pygments.lexers.other import BatchLexer
    from pygments.lexers.other import HtmlLexer
    from pygments.lexers.compiled import CythonLexer
    from pygments.lexers.web import XmlLexer
    from pygments.lexers.dotnet import BooLexer
    from pygments.lexers.text import MakefileLexer
    from pygments.lexers.text import CMakeLexer
    from pygments.lexers.text import RstLexer
    from pygments.lexers.web import JsonLexer

    from pygments.lexers.dotnet import CSharpLexer
    from pygments.lexers.web import ActionScriptLexer
    from pygments.lexers.web import CoffeeScriptLexer
    from pygments.lexers.web import CssLexer
    from pygments.lexers.web import JavascriptLexer
    from pygments.lexers.jvm import JavaLexer
    from pygments.lexers.web import QmlLexer
    from pygments.lexers.web import PhpLexer
    from pygments.lexers.compiled import AdaLexer
    from pygments.lexers.compiled import CLexer
    from pygments.lexers.compiled import CppLexer
    from pygments.lexers.compiled import CudaLexer
    from pygments.lexers.compiled import DLexer
    from pygments.lexers.compiled import GLShaderLexer
    from pygments.lexers.compiled import GoLexer
    from pygments.lexers.compiled import ObjectiveCLexer
    from pygments.lexers.compiled import ObjectiveCppLexer
    from pygments.lexers.compiled import ValaLexer
except ImportError as e:  # too new on some systems
    logger.error("Faile to import pygments lexer, please update your pygments "
                 "installation. %s" % e)

from pygments.styles import get_style_by_name
from pygments.token import Whitespace, Comment
from pygments.util import ClassNotFound


from pygments.styles import STYLE_MAP

#: A sorted list of available pygments styles, for convenience
PYGMENTS_STYLES = sorted(STYLE_MAP.keys())


def get_tokens_unprocessed(self, text, stack=('root',)):
    """ Split ``text`` into (tokentype, text) pairs.

        Monkeypatched to store the final stack on the object itself.
    """
    pos = 0
    tokendefs = self._tokens
    if hasattr(self, '_saved_state_stack'):
        statestack = list(self._saved_state_stack)
    else:
        statestack = list(stack)
    try:
        statetokens = tokendefs[statestack[-1]]
    except KeyError:
        self._saved_state_stack = None
        return
    while 1:
        for rexmatch, action, new_state in statetokens:
            m = rexmatch(text, pos)
            if m:
                if type(action) is _TokenType:
                    yield pos, action, m.group()
                else:
                    for item in action(self, m):
                        yield item
                pos = m.end()
                if new_state is not None:
                    # state transition
                    if isinstance(new_state, tuple):
                        for state in new_state:
                            if state == '#pop':
                                statestack.pop()
                            elif state == '#push':
                                statestack.append(statestack[-1])
                            else:
                                statestack.append(state)
                    elif isinstance(new_state, int):
                        # pop
                        del statestack[new_state:]
                    elif new_state == '#push':
                        statestack.append(statestack[-1])
                    else:
                        assert False, "wrong state def: %r" % new_state
                    statetokens = tokendefs[statestack[-1]]
                break
        else:
            try:
                if text[pos] == '\n':
                    # at EOL, reset state to "root"
                    pos += 1
                    statestack = ['root']
                    statetokens = tokendefs['root']
                    yield pos, Text, '\n'
                    continue
                yield pos, Error, text[pos]
                pos += 1
            except IndexError:
                break
    self._saved_state_stack = list(statestack)

# Monkeypatch!
RegexLexer.get_tokens_unprocessed = get_tokens_unprocessed


# Even with the above monkey patch to store state, multiline comments do not
# work since they are stateless (Pygments uses a single multiline regex for
# these comments, but Qt lexes by line). So we need to add a state for comments
# to the C and C++ lexers. This means that nested multiline comments will
# appear
# to be valid C/C++, but this is better than the alternative for now.

def replace_pattern(tokens, new_pattern):
    """ Given a RegexLexer token dictionary 'tokens', replace all patterns that
        match the token specified in 'new_pattern' with 'new_pattern'.
    """
    for state in tokens.values():
        for index, pattern in enumerate(state):
            if isinstance(pattern, tuple) and pattern[1] == new_pattern[1]:
                state[index] = new_pattern

# More monkeypatching!
comment_start = (r'/\*', Comment.Multiline, 'comment')
comment_state = [(r'[^*/]', Comment.Multiline),
                 (r'/\*', Comment.Multiline, '#push'),
                 (r'\*/', Comment.Multiline, '#pop'),
                 (r'[*/]', Comment.Multiline)]
replace_pattern(CLexer.tokens, comment_start)
replace_pattern(CppLexer.tokens, comment_start)
CLexer.tokens['comment'] = comment_state
CppLexer.tokens['comment'] = comment_state
CSharpLexer.tokens['comment'] = comment_state


class PygmentsSyntaxHighlighter(SyntaxHighlighter):
    """
    This mode enable syntax highlighting using the pygments library

    Here the properties added by the mode to
    :attr:`pyqode.core.QCodeEdit.style`:

    ====================== ====================== ======= ====================== =====================
    Key                    Section                Type    Default value          Description
    ====================== ====================== ======= ====================== =====================
    pygmentsStyle          General                QColor  Computed.              Background color for matching symbols
    ====================== ====================== ======= ====================== =====================

    .. warning:: There are some issues with multi-line comments, they are not
                 properly highlighted until a full re-highlight is triggered.
                 The text is automatically re-highlighted on save.
    """
    #: Mode description
    DESCRIPTION = "Apply syntax highlighting to the editor using pygments"

    #: Associates a fold detector to a specific pygments lexer.
    try:
        LEXERS_FOLD_DETECTORS = {
            # indent based
            PythonLexer: IndentBasedFoldDetector(),
            CythonLexer: IndentBasedFoldDetector(),
            BashLexer: IndentBasedFoldDetector(),
            BatchLexer: IndentBasedFoldDetector(),
            XmlLexer: IndentBasedFoldDetector(),
            HtmlLexer: IndentBasedFoldDetector(),
            JsonLexer: IndentBasedFoldDetector(),
            BooLexer: IndentBasedFoldDetector(),
            MakefileLexer: IndentBasedFoldDetector(),
            CMakeLexer: IndentBasedFoldDetector(),
            RstLexer: IndentBasedFoldDetector(),

            # c family
            CLexer: CharBasedFoldDetector(),
            CppLexer: CharBasedFoldDetector(),
            CSharpLexer: CharBasedFoldDetector(),
            ActionScriptLexer: CharBasedFoldDetector(),
            CoffeeScriptLexer: CharBasedFoldDetector(),
            CssLexer: CharBasedFoldDetector(),
            JavascriptLexer: CharBasedFoldDetector(),
            JavaLexer: CharBasedFoldDetector(),
            QmlLexer: CharBasedFoldDetector(),
            PhpLexer: CharBasedFoldDetector(),
            AdaLexer: CharBasedFoldDetector(),
            CudaLexer: CharBasedFoldDetector(),
            DLexer: CharBasedFoldDetector(),
            GLShaderLexer: CharBasedFoldDetector(),
            GoLexer: CharBasedFoldDetector(),
            ObjectiveCLexer: CharBasedFoldDetector(),
            ObjectiveCppLexer: CharBasedFoldDetector(),
            ValaLexer: CharBasedFoldDetector(),
        }
    except NameError:
        logger.warning("PygmentsSyntaxHighlighter: Failed to setup fold "
                       "detectors associations. Please upgrade your pygments "
                       "installation.")
        LEXERS_FOLD_DETECTORS = {}

    @property
    def pygmentsStyle(self):
        return self.editor.style.value("pygmentsStyle")

    @pygmentsStyle.setter
    def pygmentsStyle(self, value):
        return self.editor.style.setValue("pygmentsStyle", value)

    def __init__(self, document, lexer=None):
        super(PygmentsSyntaxHighlighter, self).__init__(document)
        self._document = QtGui.QTextDocument()
        self._formatter = HtmlFormatter(nowrap=True)
        self._lexer = lexer if lexer else PythonLexer()
        self.__previousFilename = ""
        self.style = "default"

    def _onInstall(self, editor):
        """
        :type editor: pyqode.code.QCodeEdit
        """
        SyntaxHighlighter._onInstall(self, editor)
        self.triggers = ["*", '**', '"', "'", "/"]
        self._clear_caches()
        self.prev_txt = ""
        style = editor.style.addProperty("pygmentsStyle", "default")
        self.style = style
        self.editor.style.setValue(
                    "background",
                    QtGui.QColor(self.style.background_color))
        c = self.style.style_for_token(Text)['color']
        if c is None:
            c = '000000'
        self.editor.style.setValue(
            "foreground", QtGui.QColor("#{0}".format(c)))

    def _onStateChanged(self, state):
        self.enabled = state
        if state is True:
            self.editor.textSaved.connect(self.rehighlight)
        else:
            self.editor.textSaved.disconnect(self.rehighlight)
        self.rehighlight()

    def __updateLexer(self):
        self.setLexerFromFilename(self.editor.fileName)
        if hasattr(self.editor, "foldingPanel"):
            if type(self._lexer) in self.LEXERS_FOLD_DETECTORS:
                self.setFoldDetector(
                    self.LEXERS_FOLD_DETECTORS[type(self._lexer)])
                self.editor.foldingPanel.enabled = True
            else:
                self.editor.foldingPanel.enabled = False

    def __onTextSaved(self):
        self.rehighlight()

    def _onStyleChanged(self, section, key):
        """ Updates the pygments style """
        if key == "pygmentsStyle" or not key:
            self.style = self.editor.style.value(
                "pygmentsStyle")
            self.rehighlight()
            self.editor.style.setValue(
                "background",
                QtGui.QColor(self.style.background_color))
            c = self.style.style_for_token(Text)['color']
            if c is None:
                c = '000000'
            self.editor.style.setValue(
                "foreground", QtGui.QColor("#{0}".format(c)))

    def setLexerFromFilename(self, filename):
        """
        Change the lexer based on the filename (actually only the extension is
        needed)

        :param filename: Filename or extension
        """
        try:
            if filename.endswith("~"):
                filename = filename[0:len(filename) - 1]
            self._lexer = get_lexer_for_filename(filename)
        except ClassNotFound:
            logger.warning("Failed to find lexer from filename %s" % filename)
            self._lexer = None

    def setLexerFromMimeType(self, mime, **options):
        try:
            self._lexer = get_lexer_for_mimetype(mime, **options)
        except ClassNotFound:
            logger.warning("Failed to find lexer from mime type %s" % mime)
            self._lexer = None

    def doHighlightBlock(self, text):
        fn = self.editor.fileName
        if fn != self.__previousFilename:
            self.__previousFilename = fn
            self.__updateLexer()
        if self._lexer is None:
            return

        #Spaces
        expression = QRegExp('\s+')
        index = expression.indexIn(text, 0)
        while index >= 0:
            index = expression.pos(0)
            length = len(expression.cap(0))
            self.setFormat(index, length, self._get_format(Whitespace))
            index = expression.indexIn(text, index + length)

        if self.enabled is False:
            return
        prev_data = self.currentBlock().previous().userData()

        if hasattr(prev_data, "syntax_stack"):
            self._lexer._saved_state_stack = prev_data.syntax_stack
        elif hasattr(self._lexer, '_saved_state_stack'):
            del self._lexer._saved_state_stack

        # Lex the text using Pygments
        index = 0
        for token, text in self._lexer.get_tokens(text):
            length = len(text)
            if "string" in str(token).lower() or \
                    "comment" in str(token).lower():
                self.setCurrentBlockState(1)
            self.setFormat(index, length, self._get_format(token))
            index += length

        if hasattr(self._lexer, '_saved_state_stack'):
            data = self.currentBlock().userData()
            setattr(data, "syntax_stack", self._lexer._saved_state_stack)
            self.currentBlock().setUserData(data)
            # Clean up for the next go-round.
            del self._lexer._saved_state_stack

    def __set_style(self, style):
        """ Sets the style to the specified Pygments style.
        """
        if (isinstance(style, str) or
                isinstance(style, unicode)):
            style = get_style_by_name(style)
        self._style = style
        self._clear_caches()

    def __get_style(self):
        return self._style

    #: gets/sets the **pygments** style.
    style = property(__get_style, __set_style)

    def _clear_caches(self):
        """ Clear caches for brushes and formats.
        """
        self._brushes = {}
        self._formats = {}

    def _get_format(self, token):
        """ Returns a QTextCharFormat for token or None.
        """
        if token in self._formats:
            return self._formats[token]

        if self._style is None:
            result = self._get_format_from_document(token, self._document)
        else:
            result = self._get_format_from_style(token, self._style)

        self._formats[token] = result
        return result

    def _get_format_from_document(self, token, document):
        """ Returns a QTextCharFormat for token by
        """
        code, html = next(self._formatter._format_lines([(token, 'dummy')]))
        self._document.setHtml(html)
        return QtGui.QTextCursor(self._document).charFormat()

    def _get_format_from_style(self, token, style):
        """ Returns a QTextCharFormat for token by reading a Pygments style.
        """
        result = QtGui.QTextCharFormat()
        for key, value in list(style.style_for_token(token).items()):
            if value:
                if key == 'color':
                    result.setForeground(self._get_brush(value))
                elif key == 'bgcolor':
                    result.setBackground(self._get_brush(value))
                elif key == 'bold':
                    result.setFontWeight(QtGui.QFont.Bold)
                elif key == 'italic':
                    result.setFontItalic(True)
                elif key == 'underline':
                    result.setUnderlineStyle(
                        QtGui.QTextCharFormat.SingleUnderline)
                elif key == 'sans':
                    result.setFontStyleHint(QtGui.QFont.SansSerif)
                elif key == 'roman':
                    result.setFontStyleHint(QtGui.QFont.Times)
                elif key == 'mono':
                    result.setFontStyleHint(QtGui.QFont.TypeWriter)
        return result

    def _get_brush(self, color):
        """ Returns a brush for the color.
        """
        result = self._brushes.get(color)
        if result is None:
            qcolor = self._get_color(color)
            result = QtGui.QBrush(qcolor)
            self._brushes[color] = result
        return result

    @staticmethod
    def _get_color(color):
        """ Returns a QColor built from a Pygments color string.
        """
        color = str(color).replace("#", "")
        qcolor = QtGui.QColor()
        qcolor.setRgb(int(color[:2], base=16),
                      int(color[2:4], base=16),
                      int(color[4:6], base=16))
        return qcolor
