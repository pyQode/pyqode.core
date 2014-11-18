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


from test.helpers import editor_open
from pyqode.core.api import TextHelper
from pyqode.core import modes
from pyqode.qt import QtGui



def get_mode(editor):
    return editor.modes.get(modes.SymbolMatcherMode)


def test_enabled(editor):
    mode = get_mode(editor)
    assert mode.enabled
    mode.enabled = False
    mode.enabled = True


def test_properties(editor):
    mode = get_mode(editor)
    c = QtGui.QColor('yellow')
    assert isinstance(mode.match_background, QtGui.QBrush)
    mode.match_background = c
    assert mode.match_background.name() == c.name()

    assert isinstance(mode.match_foreground, QtGui.QColor)
    mode.match_foreground = c
    assert mode.match_foreground.name() == c.name()

    assert isinstance(mode.unmatch_background, QtGui.QBrush)
    mode.unmatch_background = c
    assert mode.unmatch_background.name() == c.name()

    assert isinstance(mode.unmatch_foreground, QtGui.QColor)
    mode.unmatch_foreground = c
    assert mode.unmatch_foreground.name() == c.name()


@editor_open(__file__)
def test_matching(editor):
    """
    Moves the text cursor in a few places to execute all statements in
    matcher.py.

    """
    mode = get_mode(editor)
    # before [
    TextHelper(editor).goto_line(1, 14)
    mode.do_symbols_matching()
    # after ]
    TextHelper(editor).goto_line(4, 1)
    mode.do_symbols_matching()
    # before {
    TextHelper(editor).goto_line(5, 14)
    mode.do_symbols_matching()
    # after }
    TextHelper(editor).goto_line(8, 1)
    mode.do_symbols_matching()
    # before (
    TextHelper(editor).goto_line(9, 16)
    mode.do_symbols_matching()
    # after )
    TextHelper(editor).goto_line(12, 1)
    mode.do_symbols_matching()


malformed_symbols_code = """a = [
b = {
c = (
"""


@editor_open(__file__)
def test_unmatching(editor):
    mode = get_mode(editor)
    # for this test we need to load uncorrect code with non matching symbols
    editor.setPlainText(malformed_symbols_code, 'text/x-python', 'utf-8')
    TextHelper(editor).goto_line(0, 4)
    mode.do_symbols_matching()
    TextHelper(editor).goto_line(1, 4)
    mode.do_symbols_matching()
    TextHelper(editor).goto_line(2, 4)
    mode.do_symbols_matching()


cplx_code = """
a = [([1, 2, (45, 3)]), ({2: (45, 10)}),
     ({2: {3: (4, 5)}}, 10)]
]
"""


@editor_open(__file__)
def test_complex_matching(editor):
    mode = get_mode(editor)
    # [
    editor.setPlainText(cplx_code, 'text/x-python', 'utf-8')
    TextHelper(editor).goto_line(1, 4)
    mode.do_symbols_matching()
    # ]
    TextHelper(editor).goto_line(2, 28)
    mode.do_symbols_matching()
    # {
    TextHelper(editor).goto_line(2, 6)
    mode.do_symbols_matching()
    # }
    TextHelper(editor).goto_line(2, 22)
    mode.do_symbols_matching()
    # (
    TextHelper(editor).goto_line(2, 5)
    mode.do_symbols_matching()
    # )
    TextHelper(editor).goto_line(2, 27)
    mode.do_symbols_matching()


@editor_open(__file__)
def test_symbol_pos(editor):
    """
    Moves the text cursor in a few places to execute all statements in
    matcher.py.

    """
    mode = get_mode(editor)
    editor.file.open(__file__)
    # move to ')'
    cursor = TextHelper(editor).goto_line(12, 1, move=False)
    l, c = mode.symbol_pos(cursor)
    assert l == 9
    assert c == 17
