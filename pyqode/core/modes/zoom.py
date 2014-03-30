# -*- coding: utf-8 -*-
from pyqode.core.api import constants
from pyqode.core.editor import Mode
from PyQt4 import QtCore


class ZoomMode(Mode):
    """
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

    def _on_state_changed(self, state):
        """
        Connects/Disconnects to the mouse_wheel_activated and key_pressed event
        """
        if state:
            self.editor.mouse_wheel_activated.connect(
                self._on_wheel_event)
            self.editor.key_pressed.connect(self._on_key_pressed)
        else:
            self.editor.mouse_wheel_activated.disconnect(
                self._on_wheel_event)
            self.editor.key_pressed.disconnect(self._on_key_pressed)

    def _on_key_pressed(self, event):
        """
        Resets editor font size to the default font size

        :param event: wheelEvent
        :type event: QKeyEvent
        """
        if int(event.modifiers()) & QtCore.Qt.ControlModifier > 0:
            if event.key() == QtCore.Qt.Key_0:
                self.editor.reset_zoom()
                event.accept()
            if event.key() == QtCore.Qt.Key_Plus:
                self.editor.zoom_in()
                event.accept()
            if event.key() == QtCore.Qt.Key_Minus:
                self.editor.zoom_out()
                event.accept()

    def _on_wheel_event(self, event):
        """
        Increments or decrements editor fonts settings on mouse wheel event
        if ctrl modifier is on.

        :param event: wheel event
        :type event: QWheelEvent
        """
        delta = event.delta()
        if int(event.modifiers()) & QtCore.Qt.ControlModifier > 0:
            if delta < self.prev_delta:
                self.editor.zoom_out()
                event.accept()
            else:
                self.editor.zoom_in()
                event.accept()
