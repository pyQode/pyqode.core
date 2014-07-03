# -*- coding: utf-8 -*-
"""
This module contains the CodeEdit designer plugin.
"""
from pyqode.core.designer_plugins import WidgetPlugin
# pylint: disable=missing-docstring, invalid-name, interface-not-implemented
from pyqode.core.api import CodeEdit


class CodeEditPlugin(WidgetPlugin):
    """
    Designer plugin for CodeEdit.
    """
    def klass(self):
        return CodeEdit

    def objectName(self):
        return 'codeEdit'
