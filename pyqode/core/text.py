"""
This module contains the text API, a set of functions that expands the
Qt text API specifially for code manipulations.

The API is made up of a set of utility functions to help you manipulate
the content of a QCodeEdit programmatically (functions to select text, move
cursor easily, indent, check if the cursor is between parenthesis,...).

All those functions will take a QCodeEdit instance as the first parameter. (
originally all those functions were part of the QCodeEdit class, we decided to
move them to a separate module to improve readability and separation of
concerns).

"""


def goto_line(editor, line, column=0, move=True):
    """
    Moves the text cursor to the specified line (and column).

    :param line: Number of the line to go to (1 based)
    :param column: Optional column number. Default start of line.
    :param move: True to move the cursor. False will return the cursor
                 without setting it on the editor.
    :return: The new text cursor
    :rtype: QtGui.QTextCursor
    """
    tc = editor.textCursor()
    tc.movePosition(tc.Start, tc.MoveAnchor)
    tc.movePosition(tc.Down, tc.MoveAnchor, line - 1)
    if column:
        tc.movePosition(tc.Right, tc.MoveAnchor, column)
    if move:
        editor.setTextCursor(tc)
    return tc