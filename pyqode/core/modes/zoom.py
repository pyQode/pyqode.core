# -*- coding: utf-8 -*-
"""
This module contains the ZoomMode which lets you zoom in and out the editor.
"""
from pyqode.core.api.mode import Mode
from pyqode.qt import QtCore, QtGui, QtWidgets


class ZoomMode(Mode):
    """ Zooms/Unzooms the editor (Ctrl+mouse wheel or Ctrl + 0 to reset).

    This mode make it possible to zoom in/out the editor view.

    Here are the controls:
      * **zoom out**: *ctrl+-* or *ctrl+mouse wheel backward*
      * **zoom in**: *ctrl++* or *ctrl+mouse wheel forward*
      * **reset**: *ctrl + 0*
    """
    def __init__(self):
        super(ZoomMode, self).__init__()
        self.prev_delta = 0
        self.default_font_size = 10

    def on_state_changed(self, state):
        if state:
            self.editor.mouse_wheel_activated.connect(
                self._on_wheel_event)
            self.mnu_zoom = QtWidgets.QMenu("Zoom", self.editor)
            # Zoom in
            a = QtWidgets.QAction(
                QtGui.QIcon.fromTheme('zoom-in'),
                'Zoom in',
                self.editor
            )
            a.setShortcutContext(QtCore.Qt.WidgetShortcut)
            self.mnu_zoom.addAction(a)
            a.setShortcut('Ctrl++')
            a.triggered.connect(self.editor.zoom_in)
            # Zoom out
            a = QtWidgets.QAction(
                QtGui.QIcon.fromTheme('zoom-out'),
                'Zoom out',
                self.editor
            )
            a.setShortcutContext(QtCore.Qt.WidgetShortcut)
            self.mnu_zoom.addAction(a)
            a.setShortcut('Ctrl+-')
            a.triggered.connect(self.editor.zoom_out)
            # Reset zoom
            a = QtWidgets.QAction(
                QtGui.QIcon.fromTheme('zoom-fit-best'),
                'Reset zoom',
                self.editor
            )
            a.setShortcutContext(QtCore.Qt.WidgetShortcut)
            self.mnu_zoom.addAction(a)
            a.setShortcut('Ctrl+0')
            a.triggered.connect(self.editor.reset_zoom)
            # Zoom menu
            a = self.mnu_zoom.menuAction()
            a.setIcon(QtGui.QIcon.fromTheme('zoom'))
            self.editor.add_action(a, sub_menu=None)
        else:
            self.editor.mouse_wheel_activated.disconnect(
                self._on_wheel_event)
            self.editor.remove_action(self.mnu_zoom.menuAction(),
                                      sub_menu=None)

    def _on_wheel_event(self, event):
        """
        Increments or decrements editor fonts settings on mouse wheel event
        if ctrl modifier is on.

        :param event: wheel event
        :type event: QWheelEvent
        """
        try:
            delta = event.angleDelta().y()
        except AttributeError:
            # PyQt4/PySide
            delta = event.delta()
        if int(event.modifiers()) & QtCore.Qt.ControlModifier > 0:
            if delta < self.prev_delta:
                self.editor.zoom_out()
                event.accept()
            else:
                self.editor.zoom_in()
                event.accept()
