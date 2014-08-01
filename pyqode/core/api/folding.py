"""
This module contains utility functions to manipulate the fold
tree.

"""
import sys
from pyqode.core.api.utils import TextBlockHelper


def print_tree(editor, file=sys.stdout, print_blocks=False):
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
            print('l%d: %s%s %s' %
                  (block.blockNumber() + 1, lvl * 4 * ' ', trigger, lvl),
                  file=file)
        elif print_blocks:
            print('l%d: %s %s' %
                  (block.blockNumber() + 1, lvl * 4 * ' ', lvl), file=file)
        block = block.next()


class Scope:
    """
    Utility class for manipulating foldable code scope (fold/unfold,
    get range, child and parent scopes and so on).

    A scope is built from a fold trigger (QTextBlock).
    """

    @property
    def trigger_level(self):
        """
        Returns the fold level of the block trigger
        :return:
        """
        return TextBlockHelper.get_fold_lvl(self._trigger)

    @property
    def scope_level(self):
        """
        Returns the fold level of the first block of the foldable scope (
        just after the trigger)

        :return:
        """
        return TextBlockHelper.get_fold_lvl(self._trigger.next())

    @property
    def collapsed(self):
        """
        Whether the scope is collasped.

        """
        return TextBlockHelper.get_fold_trigger_state(self._trigger)

    def __init__(self, block):
        """
        Create a foldable region from a fold trigger block.

        :param block: The block **must** be a fold trigger.
        :type block: QTextBlock
        """
        assert TextBlockHelper.is_fold_trigger(block)
        self._trigger = block

    def get_range(self, ignore_blank_lines=True):
        """
        Get the fold region range (start and end line).

        .. note:: Start line do no encompass the trigger line.
        """
        ref_lvl = self.trigger_level
        first_line = self._trigger.blockNumber() + 1
        block = self._trigger.next()
        last_line = block.blockNumber() + 1
        lvl = self.scope_level
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
        TextBlockHelper.set_fold_trigger_state(self._trigger, True)
        block = self._trigger.next()
        while block.blockNumber() < end:
            block.setVisible(False)
            if recursively and TextBlockHelper.is_fold_trigger(block):
                TextBlockHelper.set_fold_trigger_state(self._trigger, True)
            block = block.next()

    def unfold(self):
        """
        Unfolds the region.
        """
        # set all direct child blocks which are not triggers to be visible
        self._trigger.setVisible(True)
        TextBlockHelper.set_fold_trigger_state(self._trigger, False)
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
                block = self._trigger.document().findBlockByNumber(start - 1)
                block.setVisible(True)
                block = self._trigger.document().findBlockByNumber(bend - 1)
                while block.blockNumber() > bstart - 1:
                    block.setVisible(True)
                    block = block.previous()

    def blocks(self, ignore_blank_lines=True):
        """
        This generator generates the list of blocks directly under the fold
        region. This list does not contain blocks from child regions.

        """
        start, end = self.get_range(ignore_blank_lines=ignore_blank_lines)
        block = self._trigger.next()
        ref_lvl = self.scope_level
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
        block = self._trigger.next()
        ref_lvl = self.scope_level
        while block.blockNumber() < end and block.isValid():
            lvl = TextBlockHelper.get_fold_lvl(block)
            trigger = TextBlockHelper.is_fold_trigger(block)
            if lvl == ref_lvl and trigger:
                yield Scope(block)
            block = block.next()

    def parent(self):
        """
        Return the parent scope.

        :return: Scope or None
        """
        if TextBlockHelper.get_fold_lvl(self._trigger) > 0:
            block = self._trigger.previous()
            ref_lvl = self.trigger_level - 1
            while (block.blockNumber() and
                    (not TextBlockHelper.is_fold_trigger(block) or
                    TextBlockHelper.get_fold_lvl(block) > ref_lvl)):
                block = block.previous()
            return Scope(block)
        return None
