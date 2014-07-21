"""
Regroup functions common to all examples.
"""
import sys
import os
from pyqode.core import api


def get_file_path():
    if len(sys.argv) == 2 and os.path.exists(sys.argv[1]):
        path = sys.argv[1]
    else:
        # default to a file encoded with big5 encoding (chinese).
        path = os.path.abspath(
            os.path.join('..', '..', 'test', 'files', 'big5hkscs.txt'))
    return path


def setup_editor(modes=None, panels=None, encoding=None):
    path = get_file_path()
    editor = api.CodeEdit()
    editor.setMinimumSize(800, 600)
    editor.show()
    if modes:
        for mode in modes:
            editor.modes.append(mode)
    if panels:
        for panel, position in panels:
            editor.panels.append(panel, position)
    # Do not use cache for the example so you can retry. This should be left to
    # True in real apps.
    editor.file.open(path, encoding=encoding, use_cached_encoding=False)
    return editor
