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
    print('----------------------')
