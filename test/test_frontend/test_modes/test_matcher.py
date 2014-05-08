# the following variable are there to test the symbol matcher
example_lst = [
    1,
    2
]
example_dic = {
    1: None,
    2: None
}
example_tuple = (
    1,
    2
)


from PyQt4 import QtCore
from PyQt4 import QtGui
from PyQt4.QtTest import QTest
from pyqode.core import frontend
from pyqode.core.frontend import modes


editor = None
mode = modes.SymbolMatcherMode()


def setup_module():
    global editor, mode
    editor = frontend.CodeEdit()
    editor.setMinimumWidth(800)
    editor.setMinimumWidth(600)
    frontend.install_mode(
        editor, modes.PygmentsSyntaxHighlighter(editor.document()))
    frontend.install_mode(editor, mode)
    frontend.open_file(editor, __file__)
    editor.show()
    QTest.qWait(500)


def test_enabled():
    global mode
    assert mode.enabled
    mode.enabled = False
    mode.enabled = True


def test_properties():
    c = QtGui.QColor('yellow')
    assert isinstance(mode.match_background, QtGui.QColor)
    mode.match_background = c
    assert mode.match_background.name() == c.name()

    assert isinstance(mode.match_foreground, QtGui.QColor)
    mode.match_foreground = c
    assert mode.match_foreground.name() == c.name()

    assert isinstance(mode.unmatch_background, QtGui.QColor)
    mode.unmatch_background = c
    assert mode.unmatch_background.name() == c.name()

    assert isinstance(mode.unmatch_foreground, QtGui.QColor)
    mode.unmatch_foreground = c
    assert mode.unmatch_foreground.name() == c.name()

    editor.refresh_style()
    assert mode.match_background.name() != c.name()
    assert mode.match_foreground.name() != c.name()
    assert mode.unmatch_background.name() != c.name()
    assert mode.unmatch_foreground.name() != c.name()


def test_matching():
    """
    Moves the text cursor in a few places to execute all statements in
    matcher.py.

    """
    # before [
    frontend.goto_line(editor, 2, 14)
    mode.do_symbols_matching()
    # after ]
    frontend.goto_line(editor, 5, 1)
    mode.do_symbols_matching()
    # before {
    frontend.goto_line(editor, 6, 14)
    mode.do_symbols_matching()
    # after }
    frontend.goto_line(editor, 9, 1)
    mode.do_symbols_matching()
    # before (
    frontend.goto_line(editor, 10, 16)
    mode.do_symbols_matching()
    # after )
    frontend.goto_line(editor, 13, 1)
    mode.do_symbols_matching()
    editor.refresh_style()


malformed_symbols_code = """a = [
b = {
c = (
"""


def test_unmatching():
    # for this test we need to load uncorrect code with non matching symbols
    editor.setPlainText(malformed_symbols_code, 'text/x-python', 'utf-8')
    frontend.goto_line(editor, 1, 4)
    mode.do_symbols_matching()
    frontend.goto_line(editor, 2, 4)
    mode.do_symbols_matching()
    frontend.goto_line(editor, 3, 4)
    mode.do_symbols_matching()
    editor.refresh_style()


cplx_code = """
a = [([1, 2, (45, 3)]), ({2: (45, 10)}),
     ({2: {3: (4, 5)}}, 10)]
]
"""


def test_complex_matching():
    # [
    editor.setPlainText(cplx_code, 'text/x-python', 'utf-8')
    frontend.goto_line(editor, 2, 4)
    mode.do_symbols_matching()
    # ]
    frontend.goto_line(editor, 3, 28)
    mode.do_symbols_matching()
    # {
    frontend.goto_line(editor, 3, 6)
    mode.do_symbols_matching()
    # }
    frontend.goto_line(editor, 3, 22)
    mode.do_symbols_matching()
    # (
    frontend.goto_line(editor, 3, 5)
    mode.do_symbols_matching()
    # )
    frontend.goto_line(editor, 3, 27)
    mode.do_symbols_matching()


def test_symbol_pos():
    """
    Moves the text cursor in a few places to execute all statements in
    matcher.py.

    """
    frontend.open_file(editor, __file__)
    # move to ')'
    cursor = frontend.goto_line(editor, 13, 1, move=False)
    l, c = mode.symbol_pos(cursor)
    assert l == 10
    assert c == 17
