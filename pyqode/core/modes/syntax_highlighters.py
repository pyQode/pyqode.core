# -*- coding: utf-8 -*-
"""
This module contains a series of syntax highlighters inspired from
the Spyder IDE's highlighters. All the credits must go to Pierre Raybaut, the
original author. I just adapted his code to fits with pyqode.

Each SH is associated with a mimetype it can handle.

"""
import builtins
import re
from pyqode.core.api import SyntaxHighlighter as BaseSH
from pyqode.core.qt import QtGui


def syntax_highlighter_for_mimetype(mimetype, document, color_scheme):
    """
    Returns the first syntax highlighter associated with the specified mimetype.
    If no highlighter could be found, it returns PygmentsSH as the fallback
    highlighter.

    :param mimetype:
    """
    lst = [
        TextSH,
        PythonSH
    ]
    for sh in lst:
        if sh.mimetype == mimetype:
            return sh(document, color_scheme)
    from .pygments_highlighter import PygmentsSH
    return PythonSH(document, color_scheme)


class TextSH(BaseSH):
    """Simple Text Syntax Highlighter Class (do nothing)"""
    mimetype = 'text/plain'

    def highlight_block(self, text):
        pass

#
# Python Syntax highlighters
#
def any(name, alternates):
    """Return a named group pattern matching list of alternates."""
    return "(?P<%s>" % name + "|".join(alternates) + ")"

kwlist = [
    'False',
    'None',
    'True',
    'and',
    'as',
    'assert',
    'break',
    'class',
    'continue',
    'def',
    'del',
    'elif',
    'else',
    'except',
    'finally',
    'for',
    'from',
    'global',
    'if',
    'import',
    'in',
    'is',
    'lambda',
    'nonlocal',
    'not',
    'or',
    'pass',
    'raise',
    'return',
    'try',
    'while',
    'with',
    'yield',
]


def make_python_patterns(additional_keywords=[], additional_builtins=[]):
    """Strongly inspired from idlelib.ColorDelegator.make_pat"""
    kw = r"\b" + any("keyword", kwlist+additional_keywords) + r"\b"
    builtinlist = [str(name) for name in dir(builtins)
                   if not name.startswith('_')]+additional_builtins
    builtin = r"([^.'\"\\#]\b|^)" + any("builtin", builtinlist) + r"\b"
    comment = any("comment", [r"#[^\n]*"])
    instance = any("instance", [r"\bself\b"])
    number = any("number",
                 [r"\b[+-]?[0-9]+[lLjJ]?\b",
                  r"\b[+-]?0[xX][0-9A-Fa-f]+[lL]?\b",
                  r"\b[+-]?0[oO][0-7]+[lL]?\b",
                  r"\b[+-]?0[bB][01]+[lL]?\b",
                  r"\b[+-]?[0-9]+(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?[jJ]?\b"])
    sqstring = r"(\b[rRuU])?'[^'\\\n]*(\\.[^'\\\n]*)*'?"
    dqstring = r'(\b[rRuU])?"[^"\\\n]*(\\.[^"\\\n]*)*"?'
    uf_sqstring = r"(\b[rRuU])?'[^'\\\n]*(\\.[^'\\\n]*)*(\\)$(?!')$"
    uf_dqstring = r'(\b[rRuU])?"[^"\\\n]*(\\.[^"\\\n]*)*(\\)$(?!")$'
    sq3string = r"(\b[rRuU])?'''[^'\\]*((\\.|'(?!''))[^'\\]*)*(''')?"
    dq3string = r'(\b[rRuU])?"""[^"\\]*((\\.|"(?!""))[^"\\]*)*(""")?'
    uf_sq3string = r"(\b[rRuU])?'''[^'\\]*((\\.|'(?!''))[^'\\]*)*(\\)?(?!''')$"
    uf_dq3string = r'(\b[rRuU])?"""[^"\\]*((\\.|"(?!""))[^"\\]*)*(\\)?(?!""")$'
    string = any("string", [sq3string, dq3string, sqstring, dqstring])
    ufstring1 = any("uf_sqstring", [uf_sqstring])
    ufstring2 = any("uf_dqstring", [uf_dqstring])
    ufstring3 = any("uf_sq3string", [uf_sq3string])
    ufstring4 = any("uf_dq3string", [uf_dq3string])
    return "|".join([instance, kw, builtin, comment, ufstring1, ufstring2,
                     ufstring3, ufstring4, string, number,
                     any("SYNC", [r"\n"])])

CELL_SEPARATORS = ('#%%', '# %%', '# <codecell>', '# In[')


#
# Pygments Syntax highlighter
#
class PythonSH(BaseSH):
    """Python Syntax Highlighter"""
    mimetype = 'text/x-python'

    # Syntax highlighting rules:
    PROG = re.compile(make_python_patterns(), re.S)
    IDPROG = re.compile(r"\s+(\w+)", re.S)
    ASPROG = re.compile(r".*?\b(as)\b")
    # Syntax highlighting states (from one text block to another):
    (NORMAL, INSIDE_SQ3STRING, INSIDE_DQ3STRING,
     INSIDE_SQSTRING, INSIDE_DQSTRING) = list(range(5))

    # Comments suitable for Outline Explorer
    OECOMMENT = re.compile('^(# ?--[-]+|##[#]+ )[ -]*[^- ]+')

    def __init__(self, parent, color_scheme=None):
        super().__init__(parent, color_scheme)
        self.import_statements = {}
        self.found_cell_separators = False

    def highlight_block(self, text, block):
        text = str(text)
        user_data = block.user_data
        user_data.cc_disabled_zones[:] = []
        prev_state = self.previousBlockState()
        if prev_state == self.INSIDE_DQ3STRING:
            offset = -4
            text = r'""" '+text
        elif prev_state == self.INSIDE_SQ3STRING:
            offset = -4
            text = r"''' "+text
        elif prev_state == self.INSIDE_DQSTRING:
            offset = -2
            text = r'" '+text
        elif prev_state == self.INSIDE_SQSTRING:
            offset = -2
            text = r"' "+text
        else:
            offset = 0
            prev_state = self.NORMAL

        import_stmt = None

        self.setFormat(0, len(text), self.formats["normal"])

        state = self.NORMAL
        match = self.PROG.search(text)
        while match:
            for key, value in list(match.groupdict().items()):
                if value:
                    start, end = match.span(key)
                    start = max([0, start+offset])
                    end = max([0, end+offset])
                    if key == "uf_sq3string":
                        self.setFormat(start, end-start,
                                       self.formats["docstring"])
                        state = self.INSIDE_SQ3STRING
                        user_data.cc_disabled_zones.append((start, end))
                    elif key == "uf_dq3string":
                        self.setFormat(start, end-start,
                                       self.formats["docstring"])
                        state = self.INSIDE_DQ3STRING
                        user_data.cc_disabled_zones.append((start, end))
                    elif key == "uf_sqstring":
                        self.setFormat(start, end-start,
                                       self.formats["string"])
                        state = self.INSIDE_SQSTRING
                        user_data.cc_disabled_zones.append((start, end))
                    elif key == "uf_dqstring":
                        self.setFormat(start, end-start,
                                       self.formats["string"])
                        state = self.INSIDE_DQSTRING
                        user_data.cc_disabled_zones.append((start, end))
                    else:
                        self.setFormat(start, end-start, self.formats[key])
                        if key == 'comment':
                            user_data.cc_disabled_zones.append((start, end))
                        if key == "keyword":
                            if value in ("def", "class"):
                                match1 = self.IDPROG.match(text, end)
                                if match1:
                                    start1, end1 = match1.span(1)
                                    fmt = self.formats["definition"]
                                    if value == "class":
                                        fmt.setFontWeight(QtGui.QFont.Bold)
                                    self.setFormat(start1, end1-start1, fmt)
                            elif value == "import":
                                import_stmt = text.strip()
                                # color all the "as" words on same line, except
                                # if in a comment; cheap approximation to the
                                # truth
                                if '#' in text:
                                    endpos = text.index('#')
                                else:
                                    endpos = len(text)
                                while True:
                                    match1 = self.ASPROG.match(text, end,
                                                               endpos)
                                    if not match1:
                                        break
                                    start, end = match1.span(1)
                                    self.setFormat(start, end-start,
                                                   self.formats["keyword"])

            match = self.PROG.search(text, match.end())

        self.setCurrentBlockState(state)

        if import_stmt is not None:
            block_nb = self.currentBlock().blockNumber()
            self.import_statements[block_nb] = import_stmt

    def get_import_statements(self):
        return list(self.import_statements.values())

    def rehighlight(self):
        self.import_statements = {}
        self.found_cell_separators = False
        super().rehighlight()

