"""
This module contains API base classes.
"""
import weakref
from PyQt4 import QtGui
from pyqode.core import logger


class Mode(object):
    """
    Base class for editor extensions. An extension is a "thing" that can be
    installed on a editor to add new behaviours or to modify the
    appearance.

    A mode is added to a editor by using the
    :meth:`pyqode.core.editor.installMode` or
    :meth:`pyqode.core.editor.installPanel` methods.

    Subclasses must/should override the following methods:
        - :meth:`pyqode.core.Mode._on_state_changed`
        - :meth:`pyqode.core.Mode.refresh_style`
        - :meth:`pyqode.core.Mode.refresh_settings`

    The mode will be identified by its class name, this means that there cannot
    be two modes of the same type on a editor (you have to subclass it)
    """
    @property
    def editor(self):
        """
        Provides easy access to the parent editor widget (weakref)

        **READ ONLY**

        :type: pyqode.core.editor.editor
        """
        if self._editor is not None:
            return self._editor()
        else:
            return None

    @property
    def enabled(self):
        """
        Tell if the mode is enabled, :meth:`pyqode.core.Mode._onStateChanged`
        is called when the value changed.

        :type: bool
        """
        return self._enabled

    @enabled.setter
    def enabled(self, enabled):
        if enabled != self._enabled:
            self._enabled = enabled
            self._on_state_changed(enabled)

    def __init__(self):
        #: Mode name/identifier. :class:`pyqode.core.editor` use it as the
        #: attribute key when you install a mode.
        self.name = self.__class__.__name__
        #: Mode description
        self.description = self.__doc__
        self._enabled = False
        self._editor = None

    def __str__(self):
        """
        Returns the extension name
        """
        return self.name

    def _on_install(self, editor):
        """
        Installs the extension on the editor. Subclasses might want to override
        this method to add new style/settings properties to the editor.

        .. note:: This method is called by editor when you install a Mode.
                  You should never call it yourself, even in a subclass.

        .. warning:: Don't forget to call **super** when subclassing

        :param editor: editor widget instance
        :type editor: pyqode.core.editor
        """
        self._editor = weakref.ref(editor)
        self.enabled = True

    def _on_uninstall(self):
        """
        Uninstall the mode
        """
        self.enabled = False
        self._editor = None

    def _on_state_changed(self, state):
        """
        Called when the enable state changed.

        This method does not do anything, you may override it if you need
        to connect/disconnect to the editor's signals (connect when state is
        true and disconnect when it is false).

        :param state: True = enabled, False = disabled
        :type state: bool
        """
        pass

    def refresh_style(self):
        """
        Called by editor when the user wants to refresh style options.
        """
        pass

    def refresh_settings(self):
        """
        Called by editor when the user wants to refresh settings.
        """
        pass


def install_mode(editor, mode):
    """
    Installs a mode on the editor.

    :param editor: editor instance on which the mode will be installed.
    :param mode: The mode instance to install.
    :type mode: pyqode.core.api.Mode
    """
    logger.debug('installing mode %s' % mode)
    editor._modes[mode.name] = mode
    mode._on_install(editor)


def uninstall_mode(editor, name):
    """
    Uninstalls a previously installed mode.

    :param name: The name of the mode to uninstall.
    """
    logger.debug('Uninstalling mode %s' % name)
    m = get_mode(editor, name)
    if m:
        m._on_uninstall()
        editor._modes.pop(m.name)
        return m
    return None


def get_mode(editor, name_or_klass):
    """
    Gets a mode by name.

    :param name_or_klass: The name or the class of the mode to get
    :type name_or_klass: str or type
    :rtype: pyqode.core.api.Mode
    """
    if not isinstance(name_or_klass, str):
        name_or_klass = name_or_klass.__name__
    return editor._modes[name_or_klass]


def get_modes(editor):
    """
    Returns the dictionary of modes.
    """
    return editor._modes


class Panel(QtGui.QWidget, Mode):
    """
    Base class for editor panels.

    A panel is a mode and a QWidget.

    .. note:: A disabled panel will be hidden automatically.
    """

    # todo make it an enum when python 3.4 is available
    class Position(object):
        """
        Enumerates the possible panel positions
        """
        #: Top margin
        TOP = 0
        #: Left margin
        LEFT = 1
        #: Right margin
        RIGHT = 2
        #: Bottom margin
        BOTTOM = 3

    @property
    def scrollable(self):
        """
        A scrollable panel will follow the editor's scroll-bars. Left and right
        panels follow the vertical scrollbar. Top and bottom panels follow the
        horizontal scrollbar.

        :type: bool
        """
        return self._scrollable

    @scrollable.setter
    def scrollable(self, value):
        self._scrollable = value

    def __init__(self):
        Mode.__init__(self)
        QtGui.QWidget.__init__(self)
        #: Panel order into the zone it is installed to. This value is
        #: automatically set when installing the panel but it can be changed
        #: later (negative values can also be used).
        self.order_in_zone = -1
        self._scrollable = False
        self._background_brush = None
        self._foreground_pen = None

    def _on_install(self, editor):
        """
        Extends :meth:`pyqode.core.Mode._onInstall` method to set the editor
        instance as the parent widget.

        .. warning:: Don't forget to call **super** if you override this
            method!

        :param editor: editor instance
        :type editor: pyqode.core.code_edit.editor
        """
        Mode._on_install(self, editor)
        self.setParent(editor)
        self.editor.refresh_panels()
        self._background_brush = QtGui.QBrush(QtGui.QColor(
            self.palette().window().color()))
        self._foreground_pen = QtGui.QPen(QtGui.QColor(
            self.palette().windowText().color()))

    def _on_state_changed(self, state):
        """
        Shows/Hides the Panel

        .. warning:: Don't forget to call **super** if you override this
            method!

        :param state: True = enabled, False = disabled
        :type state: bool
        """
        if not self.editor.isVisible():
            return
        if state is True:
            self.show()
        else:
            self.hide()

    def paintEvent(self, event):
        if self.isVisible():
            # fill background
            self._background_brush = QtGui.QBrush(QtGui.QColor(
                self.palette().window().color()))
            self._foreground_pen = QtGui.QPen(QtGui.QColor(
                self.palette().windowText().color()))
            painter = QtGui.QPainter(self)
            painter.fillRect(event.rect(), self._background_brush)

    def showEvent(self, *args, **kwargs):
        self.editor.refresh_panels()

    def setVisible(self, visible):
        QtGui.QWidget.setVisible(self, visible)
        self.editor.refresh_panels()


def install_panel(editor, panel, position=Panel.Position.LEFT):
    """
    Installs a panel on on the editor. You must specify the position of the
    panel (panels are rendered in one of the four document margins, see
    :class:`pyqode.core.editor.Panel.Position`.

    The panel is set as an object attribute using the panel's name as the
    key.

    :param panel: The panel instance to install
    :param position: The panel position

    :type panel: pyqode.core.api.Panel
    :type position: int
    """
    panel.order_in_zone = len(editor._panels[position])
    editor._panels[position][panel.name] = panel
    panel._on_install(editor)
    editor._update_viewport_margins()


def uninstall_panel(editor, name):
    """
    Uninstalls a previously installed panel.

    :param name: The name of the panel to uninstall

    :return: The uninstalled mode instance
    """
    logger.debug('Uninstalling panel %s' % name)
    p, zone = get_panel(editor, name, get_zone=True)
    if p:
        p._on_uninstall()
        return editor._panels[zone].pop(p.name, None)
    else:
        raise KeyError(name)


def get_panel(editor, name_or_klass, get_zone=False):
    """
    Gets a panel by name

    :param name_or_klass: Name or class of the panel to get
    :param get_zone: True to also return the zone in which the panel has
        been installed.
    """
    if not isinstance(name_or_klass, str):
        name_or_klass = name_or_klass.__name__
    for i in range(4):
        try:
            panel = editor._panels[i][name_or_klass]
        except KeyError:
            pass
        else:
            if get_zone:
                return panel, i
            else:
                return panel
    return None, -1


def get_panels(editor):
    """
    Returns the panels dictionary.

    :return: A dictionary of :class:`pyqode.core.Panel`
    :rtype: dict
    """
    return editor._panels
