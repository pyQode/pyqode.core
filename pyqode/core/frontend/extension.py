"""
This module contains API base classes.
"""
import logging
import weakref
from pyqode.qt import QtWidgets, QtGui


def _logger():
    """ Returns module's logger """
    return logging.getLogger(__name__)


class Mode(object):
    """
    Base class for editor extensions. An extension is a "thing" that can be
    installed on an editor to add new behaviours or to modify the
    appearance.

    A mode is added to an editor by using
    :meth:`pyqode.core.frontend.install_mode` or
    :meth:`pyqode.core.frontend.install_panel`.

    Subclasses may/should override the following methods:
        - :meth:`pyqode.core.frontend.Mode._on_state_changed`
        - :meth:`pyqode.core.frontend.Mode.refresh_style`
        - :meth:`pyqode.core.frontend.Mode.refresh_settings`
        - :meth:`pyqode.core.frontend.Mode.refresh_actions`

    The mode will be identified by its class name, this means that there cannot
    be two modes of the same type on a editor!
    """

    @property
    def editor(self):
        """
        Provides easy access to the parent editor widget (weakref)

        **READ ONLY**

        :type: pyqode.core.frontend.CodeEdit
        """
        if self._editor is not None:
            return self._editor()
        else:
            return None

    @property
    def enabled(self):
        """
        Tell if the mode is enabled,
        :meth:`pyqode.core.frontend.Mode._on_state_changed` is called when the
        state changed.

        :type: bool
        """
        return self._enabled

    @enabled.setter
    def enabled(self, enabled):
        # pylint: disable=missing-docstring
        if enabled != self._enabled:
            self._enabled = enabled
            self._on_state_changed(enabled)

    def __init__(self):
        #: Mode name/identifier. :class:`pyqode.core.frontend.CodeEdit` uses
        # that as the attribute key when you install a mode.
        self.name = self.__class__.__name__
        #: Mode description
        self.description = self.__doc__
        self._enabled = False
        self._editor = None

    def _on_install(self, editor):
        """
        Installs the extension on the editor.

        .. note:: This method is called by editor when you install a Mode.
                  You should never call it yourself, even in a subclass.

        .. warning:: Don't forget to call **super** when subclassing

        :param editor: editor widget instance
        :type editor: pyqode.core.frontend.CodeEdit
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


def install_mode(editor, mode):
    """
    Installs a mode on the editor.

    :param editor: editor instance on which the mode will be installed.
    :param mode: The mode instance to install.
    :type mode: pyqode.core.frontend.Mode
    """
    _logger().info('installing mode %r', mode.name)
    # pylint: disable=protected-access
    editor._modes[mode.name] = mode
    mode._on_install(editor)
    return mode


def uninstall_mode(editor, name):
    """
    Uninstalls a previously installed mode.

    :param name: The name of the mode to uninstall.
    """
    # pylint: disable=protected-access
    _logger().info('uninstalling mode %r', name)
    mode = get_mode(editor, name)
    mode._on_uninstall()
    editor._modes.pop(mode.name)
    return mode


def get_mode(editor, name_or_klass):
    """
    Gets a mode by name.

    :param name_or_klass: The name or the class of the mode to get
    :type name_or_klass: str or type
    :rtype: pyqode.core.frontend.Mode
    """
    # pylint: disable=protected-access
    if not isinstance(name_or_klass, str):
        name_or_klass = name_or_klass.__name__
    return editor._modes[name_or_klass]


def get_modes(editor):
    """
    Returns the dictionary of modes.
    """
    # pylint: disable=protected-access
    return editor._modes


class Panel(QtWidgets.QWidget, Mode):
    """
    Base class for editor panels.

    A panel is a mode and a QWidget.

    .. note:: A disabled panel will be hidden automatically.
    """
    class Position:  # pylint: disable=no-init, too-few-public-methods
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

        @classmethod
        def iterable(cls):
            """ Returns possible positions as an iterable (list) """
            return [cls.TOP, cls.LEFT, cls.RIGHT, cls.BOTTOM]

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
        # pylint: disable=missing-docstring
        self._scrollable = value

    def __init__(self):
        Mode.__init__(self)
        QtWidgets.QWidget.__init__(self)
        #: Panel order into the zone it is installed to. This value is
        #: automatically set when installing the panel but it can be changed
        #: later (negative values can also be used).
        self.order_in_zone = -1
        self._scrollable = False
        self._background_brush = None
        self._foreground_pen = None
        #: Position in the editor (top, left, right, bottom)
        self.position = -1

    def _on_install(self, editor):
        """
        Extends :meth:`pyqode.core.frontend.Mode._on_install` method to set the
        editor instance as the parent widget.

        .. warning:: Don't forget to call **super** if you override this
            method!

        :param editor: editor instance
        :type editor: pyqode.core.frontend.CodeEdit
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
        """ Fills the panel background. """
        # pylint: disable=invalid-name
        if self.isVisible():
            # fill background
            self._background_brush = QtGui.QBrush(QtGui.QColor(
                self.palette().window().color()))
            self._foreground_pen = QtGui.QPen(QtGui.QColor(
                self.palette().windowText().color()))
            painter = QtGui.QPainter(self)
            painter.fillRect(event.rect(), self._background_brush)

    def setVisible(self, visible):
        """
        Shows/Hides the panel

        Automatically call CodeEdit.refresh_panels.
        """
        # pylint: disable=invalid-name
        _logger().debug('%s visibility changed', self.name)
        QtWidgets.QWidget.setVisible(self, visible)
        self.editor.refresh_panels()


def install_panel(editor, panel, position=Panel.Position.LEFT):
    """
    Installs a panel on on the editor. You must specify the position of the
    panel (panels are rendered in one of the four document margins, see
    :class:`pyqode.core.frontend.Panel.Position`.

    The panel is set as an object attribute using the panel's name as the
    key.

    :param panel: The panel instance to install
    :param position: The panel position

    :type panel: pyqode.core.frontend.Panel
    :type position: int
    """
    # pylint: disable=protected-access
    assert panel is not None
    pos_to_string = {
        Panel.Position.BOTTOM: 'bottom',
        Panel.Position.LEFT: 'left',
        Panel.Position.RIGHT: 'right',
        Panel.Position.TOP: 'top'
    }
    _logger().info('installing panel %s at %r', panel.name,
                   pos_to_string[position])
    panel.order_in_zone = len(editor._panels[position])
    editor._panels[position][panel.name] = panel
    panel.position = position
    panel._on_install(editor)
    _logger().info('panel %s installed', panel.name)
    return panel


def uninstall_panel(editor, name):
    """
    Uninstalls a previously installed panel.

    :param name: The name of the panel to uninstall

    :return: The uninstalled mode instance
    """
    # pylint: disable=protected-access
    _logger().info('Uninstalling panel %s', name)
    panel, zone = get_panel(editor, name, get_zone=True)
    panel._on_uninstall()
    return editor._panels[zone].pop(panel.name, None)


def get_panel(editor, name_or_klass, get_zone=False):
    """
    Gets a panel by name

    :param name_or_klass: Name or class of the panel to get
    :param get_zone: True to also return the zone in which the panel has
        been installed.
    """
    # pylint: disable=protected-access
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
    raise KeyError(name_or_klass)


def get_panels(editor):
    """
    Returns the panels dictionary.

    :return: A dictionary of :class:`pyqode.core.frontend.Panel`
    :rtype: dict
    """
    # pylint: disable=protected-access
    return editor._panels


def uninstall_all(editor):
    """
    Uninstalls all modes and panels.

    :param editor: CodeEdit instance.
    """
    # pylint: disable=protected-access
    while len(editor._modes):
        key = list(editor._modes.keys())[0]
        mode = uninstall_mode(editor, key)
        del mode
    for i in range(4):
        while len(editor._panels[i]):
            key = list(editor._panels[i].keys())[0]
            panel = uninstall_panel(editor, key)
            del panel
