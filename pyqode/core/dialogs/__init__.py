"""
This package contains all the pyqode specific dialogs.

"""
from .goto import DlgGotoLine
from .encodings import DlgPreferredEncodingsEditor

__all__ = [
    'DlgPreferredEncodingsEditor',
    'DlgGotoLine'
]