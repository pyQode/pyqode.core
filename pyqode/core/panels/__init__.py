# -*- coding: utf-8 -*-
"""
This package contains the core panels
"""
# pylint: disable=unused-import
from .encodings import EncodingPanel
from .line_number import LineNumberPanel
from .marker import Marker
from .marker import MarkerPanel
from .checker import CheckerPanel
from .search_and_replace import SearchAndReplacePanel


__all__ = [
    'CheckerPanel',
    'EncodingPanel'
    'LineNumberPanel',
    'Marker',
    'MarkerPanel',
    'SearchAndReplacePanel',
]
