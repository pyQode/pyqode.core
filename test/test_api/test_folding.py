import glob
import re
import pytest
import sys
from ..helpers import delete_file_on_return, editor_open
from pyqode.core.api import folding, TextBlockHelper, TextHelper
from pyqode.qt.QtTest import QTest


class FoldDetectorTestCase(object):
    """
    Checks that the fold detector detects the corret layout when loading
    files (or setting text). Dynamic checks (i.e. when the user edit the text
    are performed by DynamicFoldDetectorTestCase).
    """
    def __init__(self, test_file, results_file):
        with open(test_file, 'r') as f:
            self.test_file_content = f.read()
        with open(results_file, 'r') as f:
            self.expected_results_content = f.read()

    @delete_file_on_return('file_structure')
    def execute(self, editor):
        editor.setPlainText(self.test_file_content, '', '')
        with open('file_structure', 'w') as f:
            folding.print_tree(editor, file=f, print_blocks=True)
        with open('file_structure', 'r') as f:
            results_content = f.read()
        assert results_content == self.expected_results_content


@pytest.mark.parametrize('case', [
    FoldDetectorTestCase('test/test_api/folding_cases/foo.py',
                         'test/test_api/folding_cases/foo.static_results')
])
def test_fold_detection_static(editor, case):
    case.execute(editor)


def test_fold_limit(editor):
    editor.syntax_highlighter.fold_detector.limit = 1
    editor.file.open('test/test_api/folding_cases/foo.py')
    block = editor.document().firstBlock()
    while block.blockNumber() < editor.blockCount() - 1:
        assert TextBlockHelper.get_fold_lvl(block) <= 1
        block = block.next()
    editor.syntax_highlighter.fold_detector.limit = sys.maxsize


def test_base_fold_indenter():
    f = folding.FoldDetector()
    with pytest.raises(NotImplementedError):
        f.detect_fold_level(None, None)


class DynamicFoldDetectorTestCase(object):
    """
    A dynamic test consists in loading a file and performing a few predefined
    actions (such as going to a specific line/column, pressing a key) and then
    comparing the results with the expected results (this part is similar to
    the static test cases)

    The case will load a context file which must contains the following three
    entries:
        - input: path relative to the root of the source dir
        - results: path relative to the root of the source dir
        - actions: one or more actions to perform (see the list below).
             each action is separated by a ';' and must be on the same line

    Here are the actions that you can perform:

        - goto_line(x, y): goto line x and column y
        - press(key): simulate a key press at the current cursor location.
                      key is the key value (e.g int(QtCore.Qt.Key_A) )
        - fold: fold the current block
        - unfold: unfold the current block
        - assert_parent: assert scope has a parent
        - assert_no_parent: assert scope has not parent
        - assert_nb_children(x): assert nb children equals x
        - assert_not_scope_start: assert the block is not the start of a fold scope

    Example::

        input: test/test_api/folding_cases/foo.py
        results: test/test_api/folding_cases/foo.dynamic_results_2
        actions:goto_line(9,0);press(16777220);fold();unfold()


    """
    def __init__(self, ctx_file):
        self._name = ctx_file
        self.file_content = None
        self.expected_results_file_content = None
        self.actions = []
        with open(ctx_file, 'r') as ctx_f:
            for l in ctx_f.read().splitlines():
                if len(l.split(':')) == 2:
                    section, value = l.split(':')
                    if section == 'input':
                        with open(value.strip(), 'r') as f:
                            self.file_content = f.read()
                    elif section == 'results':
                        with open(value.strip(), 'r') as f:
                            self.expected_results_file_content = f.read()
                    elif section == 'actions':
                        self.actions = value.strip().split(';')
        assert (len(self.file_content) and
                len(self.expected_results_file_content) and
                len(self.actions))

    def _get_scope(self, editor):
        try:
            scope = folding.FoldScope(editor.textCursor().block())
        except ValueError:
            return None
        else:
            assert len(scope.text())
            return scope

    def perform_actions(self, editor):
        for action in self.actions:
            if action.startswith('goto_line('):
                p = re.compile(r'\b\d+\b')
                matches = list(p.finditer(action))
                assert len(matches) == 2
                line = int(matches[0].group())
                column = int(matches[1].group())
                TextHelper(editor).goto_line(line - 1, column)
            elif action.startswith('press('):
                p = re.compile(r'\b\d+\b')
                matches = list(p.finditer(action))
                assert len(matches) == 1
                key = int(matches[0].group())
                QTest.keyPress(editor, key)
            elif action.startswith('assert_nb_children('):
                p = re.compile(r'\b\d+\b')
                matches = list(p.finditer(action))
                assert len(matches) == 1
                nb = int(matches[0].group())
                scope = self._get_scope(editor)
                assert len(list(scope.child_regions())) == nb
            elif action == 'fold':
                scope = self._get_scope(editor)
                scope.fold()
                assert scope.collapsed
            elif action == 'unfold':
                scope = self._get_scope(editor)
                scope.unfold()
                assert not scope.collapsed
            elif action == 'assert_parent':
                scope = self._get_scope(editor)
                assert scope.parent() is not None
            elif action == 'assert_no_parent':
                scope = self._get_scope(editor)
                assert scope.parent() is None
            elif action == 'assert_not_scope_start':
                scope = self._get_scope(editor)
                assert scope is None

    @delete_file_on_return('file_structure')
    def execute(self, editor):
        editor.setPlainText(self.file_content, '', '')
        self.perform_actions(editor)
        with open('file_structure', 'w') as f:
            folding.print_tree(editor, file=f, print_blocks=True)
        # Compare results
        with open('file_structure', 'r') as f:
            results_content = f.read()
        assert results_content == self.expected_results_file_content

    def __repr__(self):
        return self._name


@pytest.mark.parametrize('case', [
    DynamicFoldDetectorTestCase(f) for f
    in sorted(glob.glob('test/test_api/folding_cases/*.ctx'))
])
def test_fold_detection_dynamic(editor, case):
    case.execute(editor)
