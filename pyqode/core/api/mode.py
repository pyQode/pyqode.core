"""
This module contains the editor extension API.
"""
import weakref


class Mode(object):
    """
    Base class for editor extensions. An extension is a "thing" that can be
    installed on an editor to add new behaviours or to modify the
    appearance.

    A mode is added to an editor by using the ModesManager/PanelsManager:

        - :meth:`pyqode.core.api.CodeEdit.modes.append` or
        - :meth:`pyqode.core.api.CodeEdit.panels.append`

    Subclasses may/should override the following methods:

        - :meth:`pyqode.core.api.Mode.on_install`
        - :meth:`pyqode.core.api.Mode.on_uninstall`
        - :meth:`pyqode.core.api.Mode.on_state_changed`

    The mode will be identified by its class name, this means that there cannot
    be two modes of the same type on a editor!
    """

    @property
    def editor(self):
        """
        Provides easy access to the parent editor widget (weakref)

        **READ ONLY**

        :rtype: pyqode.core.api.code_edit.CodeEdit
        """
        if self._editor is not None:
            return self._editor()
        else:
            return None

    @property
    def enabled(self):
        """
        Tell if the mode is enabled,
        :meth:`pyqode.core.api.Mode.on_state_changed` is called when the
        state changed.

        :type: bool
        """
        return self._enabled

    @enabled.setter
    def enabled(self, enabled):
        if enabled != self._enabled:
            self._enabled = enabled
            self.on_state_changed(enabled)

    def __init__(self):
        #: Mode name/identifier. :class:`pyqode.core.api.CodeEdit` uses
        # that as the attribute key when you install a mode.
        self.name = self.__class__.__name__
        #: Mode description
        self.description = self.__doc__
        self._enabled = False
        self._editor = None

    def on_install(self, editor):
        """
        Installs the extension on the editor.

        :param editor: editor widget instance
        :type editor: pyqode.core.api.code_edit.CodeEdit

        .. note:: This method is called by editor when you install a Mode.
                  You should never call it yourself, even in a subclasss.

        .. warning:: Don't forget to call **super** when subclassing
        """
        self._editor = weakref.ref(editor)
        self.enabled = True

    def on_uninstall(self):
        """
        Uninstall the mode
        """
        self.enabled = False
        self._editor = None

    def on_state_changed(self, state):
        """
        Called when the enable state changed.

        This method does not do anything, you may override it if you need
        to connect/disconnect to the editor's signals (connect when state is
        true and disconnect when it is false).

        :param state: True = enabled, False = disabled
        :type state: bool
        """
        pass
