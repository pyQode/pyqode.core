# -*- coding: utf-8 -*-
"""
Test scripts for the settings module.
"""
from PyQt4 import QtGui
from pyqode.core import style
from test.helpers import preserve_style


@preserve_style
def test_whitespaces_foreground(editor):
    assert style.whitespaces_foreground.name() == QtGui.QColor(
        'light gray').name()
    style.whitespaces_foreground = QtGui.QColor('#FFFF00')
    assert editor.whitespaces_foreground.name() != QtGui.QColor(
        '#FFFF00').name()
    editor.refresh_style()
    assert editor.whitespaces_foreground.name() == QtGui.QColor(
        '#FFFF00').name()
    style.whitespaces_foreground = QtGui.QColor('light gray')
