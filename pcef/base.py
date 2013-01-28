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
    - QEditorPanel
    - QPlainCodeEdit
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


class Mode(StyledObject):
    """
    A mode is an object installable on the PCEF to provides a
    unique feature to the editor.

    To use a mode, one must install the mode on the editor widget. Installing
    a mode gives the mode a pointer to PCEF so that the mode
    can connect to various editor signals.

    For example we might have modes that connect to the paints signals to paint
    a right margin on the text edit, another mode might connect to the key
    pressed event to provides code completion or smart formatting,...


    This class is just a basic abstract interfaces to quickly creates new modes.
    """

    def __init__(self, name, description, enable=True):
        """
        :param name: The mode name
        :param description: The mode description
        :param enable: Enable/Disable the mode (enabled by default)
        """
        StyledObject.__init__(self)
        #: Mode name
        self.name = name
        #: Mode description
        self.description = description
        #: Mode enable state (subtypes should always perfrom enable state check
        #: before executing their actions)
        self.enabled = enable
        #: Editor instance
        self.editor = None

    def _onStyleChanged(self):
        pass  # not all modes need styling

    def install(self, editor):
        """
        Install the mode on the editor.

        .. warning::
            For internal use only. User should use the installMode method.

        .. warning::
            Don't forget to call **super** when subclassing

        :param editor: PCEF instance
        :type editor: pcef.editors.QGenericEditor
        """
        self.editor = editor
        self._onStyleChanged()


class QEditorPanel(QWidget, StyledObject):
    """
    Base class for panel widgets.

    A panel widget is identified by a name and is place in
    one of the four zones of the PCEF widget.
    """

    def __init__(self, name, description, parent):
        self.name = name
        self.description = description
        self.editor = None
        StyledObject.__init__(self)
        QWidget.__init__(self, parent)

    def install(self, editor):
        """
        Install the mode on the editor.

        .. warning::
            For internal use only. User should use the installPanel method.

        .. warning::
            Don't forget to call **super** when subclassing


        :param editor: PCEF instance
        :type editor: pcef.editors.QGenericEditor
        """
        self.editor = editor
        self._onStyleChanged()


class TextDecoration(QTextEdit.ExtraSelection):
    """
    Helps defining extra selection (text decorations)
    """

    def __init__(self, cursorOrBlockOrDoc,
                 startPos=None, endPos=None):
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
        """
        self.format.setUnderlineStyle(QTextCharFormat.SpellCheckUnderline)
        self.format.setUnderlineColor(color)

    def setError(self, color=Qt.red):
        """ Highlights text as a syntax error """
        self.format.setUnderlineStyle(QTextCharFormat.SpellCheckUnderline)
        self.format.setUnderlineColor(color)

    def setWarning(self, color=QColor("orange")):
        """ Highlights text as a syntax warning """
        self.format.setUnderlineStyle(QTextCharFormat.SpellCheckUnderline)
        self.format.setUnderlineColor(color)


class QCodeEditor(QWidget, StyledObject):
    """Base class for the end user editor widgets.

    QCodeEditor is a widget whose ui is setup from a Qt designer ui file.
    It embeds a QPlainCodeEdit instances (using widget promotion from the
    designer) and 4 zones to add panels.

    The editor behaviour and widgets can be enriched by installing modes and
    panels.

    The base class itself does not install any modes or panels by itself. It
    does not add actions to the text edit context menu neither. Subclasses in
    defined in the editors module will take care of that.

    .. note:: There is a filename attribute defined. This field must be view as
    a tag object to share the filename to other modules that might need this
    information. This field is only set if you use the openFileInEditor function
    (importable for the qcef package itself)
    """
    #: The default value used to for indentation. (All indentation modes should
    #  uses this value)
    TAB_SIZE = 4

    #
    # Panels zones definitions
    #
    #: Top panel zone id
    PANEL_ZONE_TOP = 0
    #: Bottom panel zone id
    PANEL_ZONE_BOTTOM = 1
    #: Left panel zone id
    PANEL_ZONE_LEFT = 2
    #: Right panel zone id
    PANEL_ZONE_RIGHT = 3

    @property
    def textEdit(self):
        """
        Return the editor plain text edit
        :return: pcef.promoted_widgets.QPlainCodeEdit
        """
        return self.ui.textEdit

    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        StyledObject.__init__(self)
        self.ui = editor_ui.Ui_Form()
        self.ui.setupUi(self)
        self.textEdit.editor = weakref.ref(self)

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

    def installPanel(self, panel, zone):
        """ Installs a panel on the widget.
        :param panel: Panel instance to install
        :param zone: The zone where the panel will be install
        QCodeEditor.PANEL_ZONE_XXX.
        """
        self.logger.info("Installing panel {0} on zone {1}".format(panel.name,
                                                                zone))
        self.panels[panel.name] = panel
        panel.install(self)
        panel.currentStyle = self.currentStyle
        self.zones[zone].addWidget(panel)

    def _onStyleChanged(self):
        """ Update installed modes and panels style. """
        self.textEdit.currentStyle = self.currentStyle
        for panel in self.panels.values():
            panel.currentStyle = self.currentStyle
        for mode in self.modes.values():
            mode.currentStyle = self.currentStyle