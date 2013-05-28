
"""
This module contains the definition of the QCodeEdit
"""
import pcef
from pcef.constants import PanelPosition, CODE_EDIT_STYLESHEET
from pcef import constants
from pcef.core.properties import PropertyRegistry


class QCodeEdit(pcef.QtGui.QPlainTextEdit):
    """
    This is the core code editor widget which inherits from a QPlainTextEdit

    The code editor provides a series of additional slots specifically suited
    for code edition:
        - keyboard events
        - mouse events
        - save / dirty events

    The widget appearance and behaviour can be customised by adding modes and
    panels (editor extensions).

    Panels are drawn in the document margin by the panel manager.

    The widget also provides a series of convenience methods to:
        - open/save a file
        - manipulate the text cursor / getting text informations (line, col,...)

    The widget exposes a style property which is a dictionary of properties
    (more about this topic in the style section)
    """

    @property
    def cursorPosition(self):
        """
        Returns the text cursor position (line, column)

        :return: The cursor position (line, column)
        :rtype: tuple(int, int)
        """
        return (self.textCursor().blockNumber() + 1,
                self.textCursor().columnNumber())

    @property
    def filename(self):
        return self.filename

    @property
    def encoding(self):
        return self.__encoding

    def __init__(self, parent=None):
        pcef.QtGui.QPlainTextEdit.__init__(self, parent)
        self.__modes = {}
        self.__panels = {PanelPosition.TOP: {},
                         PanelPosition.LEFT: {},
                         PanelPosition.RIGHT: {},
                         PanelPosition.BOTTOM: {}}

        self.settings = PropertyRegistry()
        self.settings.valueChanged.connect(self.onSettingsChanged)
        self.settings.addProperty("showWhiteSpaces", True)
        self.settings.addProperty("tabSpace", constants.TAB_SIZE)

        self.style = PropertyRegistry()
        self.style.valueChanged.connect(self.onStyleChanged)
        self.style.addProperty("font", constants.FONT)
        self.style.addProperty("fontSize", constants.FONT_SIZE)
        self.style.addProperty("background", constants.EDITOR_BACKGROUND)
        self.style.addProperty("foreground", constants.EDITOR_FOREGROUND)
        self.style.addProperty("selectionBackground",
                               constants.SELECTION_BACKGROUND)
        self.style.addProperty("selectionForeground",
                               constants.SELECTION_FOREGROUND)

        # setup style
        self.onStyleChanged("", "", "")

        self.__filename = ""
        self.__encoding = ""

        # connect slots
        self.blockCountChanged.connect(self.updateViewportMargins)

    def installMode(self, mode):
        """
        Installs a mode

        :param mode: The mode instance to install on this widget instance
        """
        self.__modes[mode.name] = mode
        mode.install(self)

    def uninstallMode(self, name):
        """
        Uninstalls a previously installed mode.

        :param name: The name of the mode to uninstall

        :return:
        """
        m = self.mode(name)
        if m:
            m.uninstall()
            self.__panels.pop(name, None)

    def mode(self, name):
        """
        Gets a mode by name

        :param name: The name of the mode to get
        :type name: str

        :rtype: pcef.Mode or None
        """
        try:
            return self.__modes[name]
        except KeyError:
            return None

    def installPanel(self, panel, position=PanelPosition.LEFT):
        """
        Install a panel on the QCodeEdit

        :param panel: The panel instance to install

        :param position: The panel position

        """
        self.__panels[position][panel.name] = panel
        panel.install(self)
        self.updateViewportMargins()

    def resizePanels(self):
        """
        Resizes panels geometries
        """
        cr = self.contentsRect()
        # takes scrolll bar into account
        vscroll_width = 0
        if self.verticalScrollBar().isVisible():
            vscroll_width = self.verticalScrollBar().width()
        hscroll_height = 0
        if self.horizontalScrollBar().isVisible():
            hscroll_height = self.horizontalScrollBar().height()
        # Top panels
        top = 0
        for panel in self.__panels[PanelPosition.TOP].values():
            sh = panel.sizeHint()
            panel.setGeometry(cr.left(), cr.top() + top,
                              cr.width() - vscroll_width,
                              sh.height())
            top += sh.height()
        # Left panels
        left = 0
        for panel in self.__panels[PanelPosition.LEFT].values():
            sh = panel.sizeHint()
            panel.setGeometry(cr.left() + left, cr.top(),
                              sh.width(), cr.height() - hscroll_height)
            left += sh.width()
        # Right panels
        right = vscroll_width
        for panel in self.__panels[PanelPosition.RIGHT].values():
            sh = panel.sizeHint()
            panel.setGeometry(cr.right() - right - sh.width(),
                              cr.top(), sh.width(), cr.height())
            right += sh.width()
        # Bottom panels
        bottom = hscroll_height
        for panel in self.__panels[PanelPosition.BOTTOM].values():
            sh = panel.sizeHint()
            panel.setGeometry(cr.left(), cr.bottom() - bottom - sh.height(),
                              cr.width(), sh.height())
            top += sh.height()

    def resizeEvent(self, e):
        """
        Resize event, lets the QPlainTextEdit handle the resize event than
        resizes the panels

        :param e: resize event
        """
        pcef.QtGui.QPlainTextEdit.resizeEvent(self, e)
        self.resizePanels()

    def updateViewportMargins(self):
        """
        Update the viewport margins depending on the installed panels
        """
        top = 0
        left = 0
        right = 0
        bottom = 0
        for panel in self.__panels[PanelPosition.TOP].values():
            top += panel.sizeHint().height()
        for panel in self.__panels[PanelPosition.LEFT].values():
            left += panel.sizeHint().width()
        for panel in self.__panels[PanelPosition.RIGHT].values():
            right += panel.sizeHint().width()
        for panel in self.__panels[PanelPosition.BOTTOM].values():
            bottom += panel.sizeHint().height()
        self.setViewportMargins(left, top, right, bottom)

    def onStyleChanged(self, section, key, value):
        """
        Resets stylesheet.

        :param section:
        :param key:
        :param value:
        """
        stylesheet = CODE_EDIT_STYLESHEET % {
            "background": self.style.value("background"),
            "foreground": self.style.value("foreground"),
            "selectionBackground": self.style.value("selectionBackground"),
            "selectionForeground": self.style.value("selectionForeground")}
        self.setStyleSheet(stylesheet)
        self.setFont(pcef.QtGui.QFont(self.style.value("font"),
                                      int(self.style.value("fontSize"))))

    def onSettingsChanged(self, section, key, value):
        pass