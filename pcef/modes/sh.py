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
"""
This module contains Syntax Highlighting mode and the QSyntaxHighlighter based on pygments
"""
from PySide.QtCore import Qt
from pcef.core import Mode
from PySide import QtGui
from pygments.lexers.compiled import CLexer, CppLexer
from PySide.QtCore import QRegExp
from PySide.QtGui import QSyntaxHighlighter
from PySide.QtGui import QTextCharFormat
from PySide.QtGui import QFont
from pygments.formatters.html import HtmlFormatter
from pygments.lexer import Error
from pygments.lexer import RegexLexer
from pygments.lexer import Text
from pygments.lexer import _TokenType
from pygments.lexers import get_lexer_for_filename
from pygments.lexers.agile import PythonLexer
from pygments.styles import get_style_by_name
from pygments.token import Whitespace, Comment
from pygments.util import ClassNotFound


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
    statetokens = tokendefs[statestack[-1]]
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
# to the C and C++ lexers. This means that nested multiline comments will appear
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


class PygmentsBlockUserData(QtGui.QTextBlockUserData):
    """ Storage for the user data associated with each line.
    """

    syntax_stack = ('root',)

    def __init__(self, **kwds):
        for key, value in kwds.items():
            setattr(self, key, value)
        QtGui.QTextBlockUserData.__init__(self)

    def __repr__(self):
        attrs = ['syntax_stack']
        kwds = ', '.join(['%s=%r' % (attr, getattr(self, attr)) for attr in attrs])
        return 'PygmentsBlockUserData(%s)' % kwds


class QPygmentsHighlighter(QSyntaxHighlighter):
    """ Syntax highlighter that uses Pygments for parsing. """

    #---------------------------------------------------------------------------
    # 'QSyntaxHighlighter' interface
    #---------------------------------------------------------------------------

    def __init__(self, parent, lexer=None):
        super(QPygmentsHighlighter, self).__init__(parent)

        self._document = QtGui.QTextDocument()
        self._formatter = HtmlFormatter(nowrap=True)
        self._lexer = lexer if lexer else PythonLexer()
        self.style = "default"
        self.enabled = True

    def setLexerFromFilename(self, filename):
        """
        Change the lexer based on the filename (actually only the extension is needed)

        :param filename: Filename or extension
        """
        try:
            self._lexer = get_lexer_for_filename(filename)
        except ClassNotFound:
            self._lexer = PythonLexer()

    def highlightBlock(self, text):
        """ Highlight a block of text """
        if self.enabled is False:
            return
        text = unicode(text)
        original_text = text
        prev_data = self.currentBlock().previous().userData()

        if prev_data is not None:
            self._lexer._saved_state_stack = prev_data.syntax_stack
        elif hasattr(self._lexer, '_saved_state_stack'):
            del self._lexer._saved_state_stack

        # Lex the text using Pygments
        index = 0
        for token, text in self._lexer.get_tokens(text):
            length = len(text)
            self.setFormat(index, length, self._get_format(token))
            index += length

        if hasattr(self._lexer, '_saved_state_stack'):
            data = PygmentsBlockUserData(
                syntax_stack=self._lexer._saved_state_stack)
            self.currentBlock().setUserData(data)
            # Clean up for the next go-round.
            del self._lexer._saved_state_stack

        # macros: $(txt)
        myClassFormat = QTextCharFormat()
        myClassFormat.setFontWeight(QFont.Bold)
        myClassFormat.setForeground(Qt.red)
        pattern = "\\$\\(\\S*\\)"
        expression = QRegExp(pattern)
        index = expression.indexIn(original_text)
        while index >= 0:
            length = expression.matchedLength()
            self.setFormat(index, length, myClassFormat)
            index = expression.indexIn(original_text, index + length)

        #Spaces
        expression = QRegExp('\s+')
        index = expression.indexIn(original_text, 0)
        while index >= 0:
            index = expression.pos(0)
            length = len(expression.cap(0))
            self.setFormat(index, length, self._get_format(Whitespace))
            index = expression.indexIn(original_text, index + length)

    #---------------------------------------------------------------------------
    # 'PygmentsHighlighter' interface
    #---------------------------------------------------------------------------
    def __set_style(self, style):
        """ Sets the style to the specified Pygments style.
        """
        if (isinstance(style, str) or
                isinstance(style, unicode)):
            style = get_style_by_name(style)
        self._style = style
        self._clear_caches()

    def set_style_sheet(self, stylesheet):
        """ Sets a CSS stylesheet. The classes in the stylesheet should
        correspond to those generated by:

            pygmentize -S <style> -f html

        Note that 'set_style' and 'set_style_sheet' completely override each
        other, i.e. they cannot be used in conjunction.
        """
        self._document.setDefaultStyleSheet(stylesheet)
        self._style = None
        self._clear_caches()

    def __get_style(self):
        return self._style

    #: gets/sets the **pygments** style.
    style = property(__get_style, __set_style)

    #---------------------------------------------------------------------------
    # Protected interface
    #---------------------------------------------------------------------------

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

    def _get_color(self, color):
        """ Returns a QColor built from a Pygments color string.
        """
        color = unicode(color).replace("#", "")
        qcolor = QtGui.QColor()
        qcolor.setRgb(int(color[:2], base=16),
                      int(color[2:4], base=16),
                      int(color[4:6], base=16))
        return qcolor


class SyntaxHighlighterMode(Mode):
    """
    This mode enable syntax highlighting (using the QPygmentsHighlighter)
    """
    #: Mode identifier
    IDENTIFIER = "Syntax highlighter"
    #: Mode description
    DESCRIPTION = "Apply syntax highlighting to the editor using "

    def __init__(self):
        self.highlighter = None
        super(SyntaxHighlighterMode, self).__init__(
            self.IDENTIFIER, self.DESCRIPTION)
        self.triggers = ["*", '"', "'", "/"]

    def install(self, editor):
        """
        :type editor: pcef.editors.QGenericEditor
        """
        self.highlighter = QPygmentsHighlighter(editor.codeEdit.document())
        self.prev_txt = ""
        super(SyntaxHighlighterMode, self).install(editor)

    def _onStateChanged(self, state):
        self.highlighter.enabled = state
        if state is True:
            self.editor.codeEdit.keyReleased.connect(self.__onKeyReleased)
        else:
            self.editor.codeEdit.keyReleased.disconnect(self.__onKeyReleased)
        self.highlighter.rehighlight()

    def __onKeyReleased(self, event):
        txt = self.editor.codeEdit.textCursor().block().text()
        if event.key() == Qt.Key_Backspace:
            for trigger in self.triggers:
                if trigger in txt or trigger in self.prev_txt:
                    self.highlighter.rehighlight()
                    break
        # Search for a triggering key
        else:
            try:
                txt = chr(event.key())
                for trigger in self.triggers:
                    if trigger in txt:
                        self.highlighter.rehighlight()
                        break
            except ValueError:
                pass  # probably a function key (arrow,...)
        self.prev_txt = txt

    def _onStyleChanged(self):
        """ Updates the pygments style """
        if self.highlighter is not None:
            self.highlighter.style = self.currentStyle.pygmentsStyle
            self.highlighter.rehighlight()

    def setLexerFromFilename(self, fn="file.py"):
        """
        Change the highlighter lexer on the fly by supplying the filename
        to highlight

        .. note::
            Actually only the file extension is needed

        .. note::
            The default lexer is the Python lexer

        :param fn: Filename or extension
        :type fn: str
        """
        assert self.highlighter is not None, "SyntaxHighlightingMode not "\
                                             "installed"
        self.highlighter.setLexerFromFilename(fn)