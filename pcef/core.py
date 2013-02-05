#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# PCEF - PySide Code Editing framework
# Copyright 2013, Colin Duquesnoy <colin.duquesnoy@gmail.com>
#
# This software is released under the LGPLv3 license.
# You should have received a copy of the GNU Lesser General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
"""
Contains the bases classes of the project:
    - StyledObject
    - Mode
    - Panel
    - CodeEdit
    - QCodeEditorBase
"""
import logging
import weakref
from PySide.QtCore import Qt
from PySide.QtGui import QWidget
from PySide.QtGui import QBoxLayout
from PySide.QtGui import QTextEdit
from PySide.QtGui import QFont
from PySide.QtGui import QTextCursor
from PySide.QtGui import QColor
from PySide.QtGui import QTextCharFormat
from PySide.QtGui import QTextFormat
from pcef.style import StyledObject
from pcef.ui import editor_ui


class EditorExtension(StyledObject):
    """
    Base class for editor extension. An extension is a "thing" that can be installed on the QCodeEditorWidget
    to add new behaviours.

    An editor extension is a :class:`pcef.style.StyledObject` as some extension might need to get access to the editor
    style and to update their brushes,...

    An editor extension is also an object that can be enabled/disabled. Its provides an enable property that
    automatically call the abstract method onStateChanged.
    """

    def __init__(self, name, description):
        """
        Creates the extension.

        :param name: Extension name (used as an identifier)

        :param description: A description of the extension (mainly used for gui (settings about the extension)).
        """
        StyledObject.__init__(self)
        #: Extension name
        self.name = name
        #: Extension description
        self.description = description
        #: Extension enables state (subclasses must implement _onStateChanged to disconnect their slots to
        # disable any actions)
        self.__enabled = False
        #: Editor instance
        self.editor = None

    def install(self, editor):
        """
        Abstract method called when the extension is installed on the editor widget.

        :param editor: editor instance.

        .. warning: Raises a NotImplementedError. Subclasses must override this method to connect to the text edit
                    signals.
        """
        raise NotImplementedError()

    def onStateChanged(self, state):
        """
        Called when the enable state changed.

        .. warning: Raises NotImplementedError. Subclasses must override this method to disconnect their slots.

        :param state: True = enabled, False = disabled
        :type state: bool
        """
        raise NotImplementedError()

    def __get_enabled(self):
        return self.__enabled

    def __set_enabled(self, enabled):
        if enabled != self.__enabled:
            self.__enabled = enabled
            self.onStateChanged(enabled)

    #: Tells whether the extension is enabled or not
    enabled = property(__get_enabled, __set_enabled)


class Mode(EditorExtension):
    """
    Base class for editor modes.

    A mode is a :class:`pcef.core.EditorExtension` that is is generally a non-visual element (not a QWidget).

    Examples of modes are Code completion, syntax highlighting,...

    To use a mode, one must install the mode on the editor widget.
    """

    def __init__(self, name, description):
        """
        Creates a Mode.

        :param name: The mode name

        :param description: The mode description
        """
        EditorExtension.__init__(self, name, description)

    def onStyleChanged(self):
        pass  # not all modes need styling

    def install(self, editor):
        """
        Install the mode on the editor.

        .. warning::
            For internal use only. User should use the installMode method.

        .. warning::
            Don't forget to call **super** when subclassing

        :param editor: editor widget instance
        :type editor: pcef.core.CodeEditorWidget
        """
        self.editor = editor
        self.onStyleChanged()


class Panel(QWidget, EditorExtension):
    """
    Base class for editor Panel widgets.

    A Panel is a QWidget and :class:`pcef.core.EditorExtension` that can be installed around the text edit widget.
    """

    def __init__(self, name, description, parent):
        EditorExtension.__init__(self, name, description)
        QWidget.__init__(self, parent)

    def install(self, editor):
        """
        Install the Panel on the editor.

        .. warning::
            For internal use only. User should use the installPanel method from :class:`pcef.core.CodeEditorWidget`

        .. warning::
            Don't forget to call **super** when subclassing


        :param editor: editor instance
        :type editor: pcef.editors.QGenericEditor
        """
        self.editor = editor
        self.onStyleChanged()

    def onStateChanged(self, state):
        """ Shows/Hides the Panel

        :param state: True = enabled, False = disabled
        :type state: bool
        """
        if state is True:
            self.show()
        else:
            self.hide()


class TextDecoration(QTextEdit.ExtraSelection):
    """
    Helper class to quickly create a text decoration.
    """

    def __init__(self, cursorOrBlockOrDoc, startPos=None, endPos=None):
        """
        Creates a text decoration

        :param cursorOrBlockOrDoc: Selection
        :type cursorOrBlockOrDoc: QTextCursor or QTextBlock or QTextDocument

        :param startPos: Selection start pos

        :param endPos: Selection end pos

        .. note:: Use the cursor selection if startPos and endPos are none.
        """
        QTextEdit.ExtraSelection.__init__(self)
        cursor = QTextCursor(cursorOrBlockOrDoc)
        if startPos is not None:
            cursor.setPosition(startPos)
        if endPos is not None:
            cursor.setPosition(endPos, QTextCursor.KeepAnchor)
        self.cursor = cursor

    def setBold(self):
        """ Uses bold text """
        self.format.setFontWeight(QFont.Bold)

    def setForeground(self, color):
        """ Sets the foreground color.
        :param color: QColor """
        self.format.setForeground(color)

    def setBackground(self, brush):
        """ Sets the background color

        :param brush: QBrush
        """
        self.format.setBackground(brush)

    def setFullWidth(self, flag=True):
        """ Sets full width selection

        :param flag: True to use full width selection.
        """
        self.cursor.clearSelection()
        self.format.setProperty(QTextFormat.FullWidthSelection, flag)

    def setSpellchecking(self, color=Qt.blue):
        """ Underlines text as a spellcheck error.

        :param color: color
        :type color: QColor
        """
        self.format.setUnderlineStyle(QTextCharFormat.SpellCheckUnderline)
        self.format.setUnderlineColor(color)

    def setError(self, color=Qt.red):
        """ Highlights text as a syntax error

        :param color: color
        :type color: QColor
        """
        self.format.setUnderlineStyle(QTextCharFormat.SpellCheckUnderline)
        self.format.setUnderlineColor(color)

    def setWarning(self, color=QColor("orange")):
        """
        Highlights text as a syntax warning

        :param color: color
        :type color: QColor
        """
        self.format.setUnderlineStyle(QTextCharFormat.SpellCheckUnderline)
        self.format.setUnderlineColor(color)


class CodeEditorWidget(QWidget, StyledObject):
    """Base class for the end user editor widgets.

    CodeEditorWidget is a :class:`PySide.QtGui.QWidget` made from a QT designer ui.

    It embeds a :class:`pcef.code_edit.CodeEdit` instance (using widget promotion from the designer) and four zones
    to add panels.

    .. note: The CodeEdit widget can be retrieved from the ui object but there is also a convenience property
             :attr:`pcef.core.CodeEditorWidget.codeEdit`

    The editor behaviour and widgets can be enriched by installing modes and panels.

    The base class itself does not install any modes or panels by itself. It does not add actions to the text edit
    context menu neither.

    Subclasses defined in the editors module will take care of that.

    You can also use the CodeEditorWidget directly and install the modes/panels/actions that you are interested in.

    .. note:: There is a filename attribute defined. This field must be view as
              a tag object to share the filename to other modules that might need this
              information. This field is only set if you use the :func:`pcef.openFileInEditor`

    """
    #: The default value used to for indentation. (All indentation modes should
    #  uses this value)
    TAB_SIZE = 4

    #
    # Panels zones definitions
    #
    #: Top Panel zone id
    PANEL_ZONE_TOP = 0
    #: Bottom Panel zone id
    PANEL_ZONE_BOTTOM = 1
    #: Left Panel zone id
    PANEL_ZONE_LEFT = 2
    #: Right Panel zone id
    PANEL_ZONE_RIGHT = 3

    @property
    def codeEdit(self):
        """
        Return the codeEdit widget

        :returns: pcef.code_edit.CodeEdit
        """
        return self.ui.codeEdit

    def __init__(self, parent=None):
        """
        Creates the widget.

        :param parent: Optional parent widget
        """
        QWidget.__init__(self, parent)
        StyledObject.__init__(self)
        self.ui = editor_ui.Ui_Form()
        self.ui.setupUi(self)
        self.codeEdit.editor = weakref.ref(self)

        #: List of installed modes
        self.modes = {}
        #: List of installed panels
        self.ui.layoutLeft.setDirection(QBoxLayout.RightToLeft)
        self.ui.layoutTop.setDirection(QBoxLayout.BottomToTop)
        self.zones = {
            self.PANEL_ZONE_TOP:    self.ui.layoutTop,
            self.PANEL_ZONE_BOTTOM: self.ui.layoutBottom,
            self.PANEL_ZONE_LEFT:   self.ui.layoutLeft,
            self.PANEL_ZONE_RIGHT:  self.ui.layoutRight}
        self.panels = {}
        self.filename = None
        self.logger = logging.getLogger(
            __name__ + "." + self.__class__.__name__)

    def installMode(self, mode):
        """ Installs a mode on the widget.

        :param mode:  Mode instance to install.
        """
        self.logger.info("Installing mode %s" % mode.name)
        self.modes[mode.name] = mode
        mode.install(self)
        mode.currentStyle = self.currentStyle
        mode.enabled = True

    def installPanel(self, panel, zone):
        """ Installs a Panel on the widget.

        :param panel: Panel instance to install

        :param zone: The zone where the Panel will be installed (CodeEditorWidget.PANEL_ZONE_XXX)
        """
        self.logger.info("Installing Panel {0} on zone {1}".format(panel.name,
                                                                zone))
        self.panels[panel.name] = panel
        panel.install(self)
        panel.currentStyle = self.currentStyle
        panel.enabled = True
        self.zones[zone].addWidget(panel)

    def onStyleChanged(self):
        """ Update installed modes and panels style. """
        self.codeEdit.currentStyle = self.currentStyle
        for panel in self.panels.values():
            panel.currentStyle = self.currentStyle
        for mode in self.modes.values():
            mode.currentStyle = self.currentStyle