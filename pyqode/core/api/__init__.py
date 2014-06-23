"""
This package contains the base classes of the API:

    - CodeEdit
    - Mode
    - Panel
    - Manager
    - TextDecoration
    - SyntaxHighlighter
    - TextBlockUserData

"""
from .code_edit import CodeEdit
from .decoration import TextDecoration
from .manager import Manager
from .mode import Mode
from .panel import Panel
from .syntax_highlighter import SyntaxHighlighter
from .syntax_highlighter import TextBlockUserData
from .utils import TextHelper
from .utils import DelayJobRunner
from .utils import TextStyle


__all__ = [
    'CodeEdit',
    'DelayJobRunner',
    'Manager',
    'Mode',
    'Panel',
    'SyntaxHighlighter',
    'TextBlockUserData',
    'TextDecoration',
    'TextHelper',
    'TextStyle'
]
