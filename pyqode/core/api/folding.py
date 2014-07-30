"""
This module contains utility functions to manipulate the fold
tree.

"""
import sys
from pyqode.core.api.utils import TextBlockHelper


def print_tree(editor, file=sys.stdout):
    """
    Prints the editor fold tree to stdout, for debugging purpose.

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
    @property
    def collapsed(self):
        return TextBlockHelper.get_fold_trigger_state(self._block)

    def __init__(self, block):
        """
        Create a foldable region from a fold trigger block.

        :param block: The block **must** be a fold trigger.
        :type block: QTextBlock
        """
        self._block = block
        assert TextBlockHelper.is_fold_trigger(block)

    def get_range(self, ignore_blank_lines=True):
        """
        Get the fold region range (start and end line).

        .. note:: Start line do no encompass the trigger line.
        """
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

    def fold(self, recursively=False):
        """
        Folds the region.

        :param recursively: Fold all sub regions.
        """
        start, end = self.get_range()
        TextBlockHelper.set_fold_trigger_state(self._block, True)
        block = self._block.next()
        while block.blockNumber() < end:
            block.setVisible(False)
            if recursively and TextBlockHelper.is_fold_trigger(block):
                TextBlockHelper.set_fold_trigger_state(self._block, True)
            block = block.next()

    def unfold(self):
        """
        Unfolds the region.
        """
        # set all direct child blocks which are not triggers to be visible
        self._block.setVisible(True)
        TextBlockHelper.set_fold_trigger_state(self._block, False)
        for block in self.blocks(ignore_blank_lines=False):
            block.setVisible(True)
        for region in self.child_regions():
            if not region.collapsed:
                region.unfold()
            else:
                # leave it closed but open the last blank lines and the
                # trigger line
                start, bstart = region.get_range(ignore_blank_lines=True)
                _, bend = region.get_range(ignore_blank_lines=False)
                block = self._block.document().findBlockByNumber(start - 1)
                block.setVisible(True)
                block = self._block.document().findBlockByNumber(bend - 1)
                while block.blockNumber() > bstart:
                    block.setVisible(True)
                    block = block.previous()

    def blocks(self, ignore_blank_lines=True):
        """
        This generator generates the list of blocks directly under the fold
        region. This list does not contain blocks from child regions.

        """
        start, end = self.get_range(ignore_blank_lines=ignore_blank_lines)
        block = self._block.next()
        ref_lvl = TextBlockHelper.get_fold_lvl(block)
        while block.blockNumber() < end and block.isValid():
            lvl = TextBlockHelper.get_fold_lvl(block)
            trigger = TextBlockHelper.is_fold_trigger(block)
            if lvl == ref_lvl and not trigger:
                yield block
            block = block.next()

    def child_regions(self):
        """
        This generator generates the list of direct child regions.
        """
        start, end = self.get_range()
        block = self._block.next()
        ref_lvl = TextBlockHelper.get_fold_lvl(block)
        while block.blockNumber() < end and block.isValid():
            lvl = TextBlockHelper.get_fold_lvl(block)
            trigger = TextBlockHelper.is_fold_trigger(block)
            if lvl == ref_lvl and trigger:
                yield FoldRegion(block)
            block = block.next()
