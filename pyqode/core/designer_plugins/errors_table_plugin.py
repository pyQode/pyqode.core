# -*- coding: utf-8 -*-
"""
This module contains the ErrorsTable designer plugin.
"""
from pyqode.core import widgets
from pyqode.core.designer_plugins import WidgetPlugin
# pylint: disable=missing-docstring, invalid-name, interface-not-implemented


class ErrorsTablePlugin(WidgetPlugin):
    """
    Designer plugin for TabWidget.
    """
    def klass(self):
        return widgets.ErrorsTable

    def objectName(self):
        return 'errorsTable'
