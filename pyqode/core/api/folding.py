"""
This module contains utility functions to manipulate the fold
tree.

"""
import sys
from pyqode.core.api.utils import TextBlockHelper


def print_tree(editor, file=sys.stdout):
    """
    Prints the editor fold tree to stdout.

    :param editor: CodeEdit instance.
    """
    block = editor.document().firstBlock()
    while block.isValid():
        trigger = TextBlockHelper().is_fold_trigger(block)
        trigger_state = TextBlockHelper().get_fold_trigger_state(block)
        lvl = TextBlockHelper().get_fold_lvl(block)
        if trigger:
            trigger = '+' if trigger_state else '-'
            print('l%d: %s%s' %
                  (block.blockNumber() + 1, lvl * 4 * ' ', trigger), file=file)
        block = block.next()


class FoldRegion:
    """
    Utility class for manipulating foldable code regions (get the range,
    iterate of blocks and sub regions).

    A code region is built from a fold trigger block or line_nbr.
    """
    def __init__(self, block):
        """
        Create a foldable region from a fold trigger block.

        :param block: The block **must** be a fold trigger.
        :type block: QTextBlock
        """
        self._block = block
        assert TextBlockHelper.is_fold_trigger(block)

    def get_range(self, ignore_blank_lines=True):
        ref_lvl = TextBlockHelper.get_fold_lvl(self._block)
        first_line = self._block.blockNumber() + 1
        block = self._block.next()
        last_line = block.blockNumber() + 1
        lvl = TextBlockHelper.get_fold_lvl(block)
        if ref_lvl == lvl:  # for zone set programmatically such as imports
                            # in pyqode.python
            ref_lvl -= 1
        while (block.isValid() and
            TextBlockHelper.get_fold_lvl(block) > ref_lvl):
            last_line = block.blockNumber() + 1
            block = block.next()

        if ignore_blank_lines:
            block = block.document().findBlockByNumber(last_line - 1)
            while block.blockNumber() and block.text().strip() == '':
                block = block.previous()
                last_line = block.blockNumber() + 1
        return first_line, last_line
