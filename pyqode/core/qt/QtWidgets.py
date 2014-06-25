import os
from pyqode.core.qt import QT_API
from pyqode.core.qt import PYQT5_API
from pyqode.core.qt import PYQT4_API
from pyqode.core.qt import PYSIDE_API

try:
    if os.environ[QT_API] == PYQT5_API:
        from PyQt5.QtWidgets import *
    elif os.environ[QT_API] == PYQT4_API:
        from PyQt4.QtGui import QAbstractButton
        from PyQt4.QtGui import QAbstractGraphicsShapeItem
        from PyQt4.QtGui import QAbstractItemDelegate
        from PyQt4.QtGui import QAbstractItemView
        from PyQt4.QtGui import QAbstractScrollArea
        from PyQt4.QtGui import QAbstractSlider
        from PyQt4.QtGui import QAbstractSpinBox
        from PyQt4.QtGui import QAction
        from PyQt4.QtGui import QActionGroup
        from PyQt4.QtGui import QApplication
        from PyQt4.QtGui import QBoxLayout
        from PyQt4.QtGui import QButtonGroup
        from PyQt4.QtGui import QCalendarWidget
        from PyQt4.QtGui import QCheckBox
        from PyQt4.QtGui import QColorDialog
        from PyQt4.QtGui import QColumnView
        from PyQt4.QtGui import QComboBox
        from PyQt4.QtGui import QCommandLinkButton
        from PyQt4.QtGui import QCommonStyle
        from PyQt4.QtGui import QCompleter
        from PyQt4.QtGui import QDataWidgetMapper
        from PyQt4.QtGui import QDateEdit
        from PyQt4.QtGui import QDateTimeEdit
        from PyQt4.QtGui import QDesktopWidget
        from PyQt4.QtGui import QDial
        from PyQt4.QtGui import QDialog
        from PyQt4.QtGui import QDialogButtonBox
        from PyQt4.QtGui import QDirModel
        from PyQt4.QtGui import QDockWidget
        from PyQt4.QtGui import QDoubleSpinBox
        from PyQt4.QtGui import QErrorMessage
        from PyQt4.QtGui import QFileIconProvider
        from PyQt4.QtGui import QFileSystemModel
        from PyQt4.QtGui import QFocusFrame
        from PyQt4.QtGui import QFontComboBox
        from PyQt4.QtGui import QFontDialog
        from PyQt4.QtGui import QFormLayout
        from PyQt4.QtGui import QFrame
        from PyQt4.QtGui import QGesture
        from PyQt4.QtGui import QGestureEvent
        from PyQt4.QtGui import QGestureRecognizer
        from PyQt4.QtGui import QGraphicsAnchor
        from PyQt4.QtGui import QGraphicsAnchorLayout
        from PyQt4.QtGui import QGraphicsBlurEffect
        from PyQt4.QtGui import QGraphicsColorizeEffect
        from PyQt4.QtGui import QGraphicsDropShadowEffect
        from PyQt4.QtGui import QGraphicsEffect
        from PyQt4.QtGui import QGraphicsEllipseItem
        from PyQt4.QtGui import QGraphicsGridLayout
        from PyQt4.QtGui import QGraphicsItem
        from PyQt4.QtGui import QGraphicsItemGroup
        from PyQt4.QtGui import QGraphicsLayout
        from PyQt4.QtGui import QGraphicsLayoutItem
        from PyQt4.QtGui import QGraphicsLineItem
        from PyQt4.QtGui import QGraphicsLinearLayout
        from PyQt4.QtGui import QGraphicsObject
        from PyQt4.QtGui import QGraphicsOpacityEffect
        from PyQt4.QtGui import QGraphicsPathItem
        from PyQt4.QtGui import QGraphicsPixmapItem
        from PyQt4.QtGui import QGraphicsPolygonItem
        from PyQt4.QtGui import QGraphicsProxyWidget
        from PyQt4.QtGui import QGraphicsRectItem
        from PyQt4.QtGui import QGraphicsRotation
        from PyQt4.QtGui import QGraphicsScale
        from PyQt4.QtGui import QGraphicsScene
        from PyQt4.QtGui import QGraphicsSceneContextMenuEvent
        from PyQt4.QtGui import QGraphicsSceneDragDropEvent
        from PyQt4.QtGui import QGraphicsSceneEvent
        from PyQt4.QtGui import QGraphicsSceneHelpEvent
        from PyQt4.QtGui import QGraphicsSceneHoverEvent
        from PyQt4.QtGui import QGraphicsSceneMouseEvent
        from PyQt4.QtGui import QGraphicsSceneMoveEvent
        from PyQt4.QtGui import QGraphicsSceneResizeEvent
        from PyQt4.QtGui import QGraphicsSceneWheelEvent
        from PyQt4.QtGui import QGraphicsSimpleTextItem
        from PyQt4.QtGui import QGraphicsTextItem
        from PyQt4.QtGui import QGraphicsTransform
        from PyQt4.QtGui import QGraphicsView
        from PyQt4.QtGui import QGraphicsWidget
        from PyQt4.QtGui import QGridLayout
        from PyQt4.QtGui import QGroupBox
        from PyQt4.QtGui import QHBoxLayout
        from PyQt4.QtGui import QHeaderView
        from PyQt4.QtGui import QInputDialog
        from PyQt4.QtGui import QItemDelegate
        from PyQt4.QtGui import QItemEditorCreatorBase
        from PyQt4.QtGui import QItemEditorFactory
        from PyQt4.QtGui import QKeyEventTransition
        from PyQt4.QtGui import QLCDNumber
        from PyQt4.QtGui import QLabel
        from PyQt4.QtGui import QLayout
        from PyQt4.QtGui import QLayoutItem
        from PyQt4.QtGui import QLineEdit
        from PyQt4.QtGui import QListView
        from PyQt4.QtGui import QListWidget
        from PyQt4.QtGui import QListWidgetItem
        from PyQt4.QtGui import QMainWindow
        from PyQt4.QtGui import QMdiArea
        from PyQt4.QtGui import QMdiSubWindow
        from PyQt4.QtGui import QMenu
        from PyQt4.QtGui import QMenuBar
        from PyQt4.QtGui import QMessageBox
        from PyQt4.QtGui import QMouseEventTransition
        from PyQt4.QtGui import QPanGesture
        from PyQt4.QtGui import QPinchGesture
        from PyQt4.QtGui import QPlainTextDocumentLayout
        from PyQt4.QtGui import QPlainTextEdit
        from PyQt4.QtGui import QProgressBar
        from PyQt4.QtGui import QProgressDialog
        from PyQt4.QtGui import QPushButton
        from PyQt4.QtGui import QRadioButton
        from PyQt4.QtGui import QRubberBand
        from PyQt4.QtGui import QScrollArea
        from PyQt4.QtGui import QScrollBar
        from PyQt4.QtGui import QShortcut
        from PyQt4.QtGui import QSizeGrip
        from PyQt4.QtGui import QSizePolicy
        from PyQt4.QtGui import QSlider
        from PyQt4.QtGui import QSpacerItem
        from PyQt4.QtGui import QSpinBox
        from PyQt4.QtGui import QSplashScreen
        from PyQt4.QtGui import QSplitter
        from PyQt4.QtGui import QSplitterHandle
        from PyQt4.QtGui import QStackedLayout
        from PyQt4.QtGui import QStackedWidget
        from PyQt4.QtGui import QStatusBar
        from PyQt4.QtGui import QStyle
        from PyQt4.QtGui import QStyleFactory
        from PyQt4.QtGui import QStyleHintReturn
        from PyQt4.QtGui import QStyleHintReturnMask
        from PyQt4.QtGui import QStyleHintReturnVariant
        from PyQt4.QtGui import QStyleOption
        from PyQt4.QtGui import QStyleOptionButton
        from PyQt4.QtGui import QStyleOptionComboBox
        from PyQt4.QtGui import QStyleOptionComplex
        from PyQt4.QtGui import QStyleOptionDockWidget
        from PyQt4.QtGui import QStyleOptionFocusRect
        from PyQt4.QtGui import QStyleOptionFrame
        from PyQt4.QtGui import QStyleOptionGraphicsItem
        from PyQt4.QtGui import QStyleOptionGroupBox
        from PyQt4.QtGui import QStyleOptionHeader
        from PyQt4.QtGui import QStyleOptionMenuItem
        from PyQt4.QtGui import QStyleOptionProgressBar
        from PyQt4.QtGui import QStyleOptionRubberBand
        from PyQt4.QtGui import QStyleOptionSizeGrip
        from PyQt4.QtGui import QStyleOptionSlider
        from PyQt4.QtGui import QStyleOptionSpinBox
        from PyQt4.QtGui import QStyleOptionTab
        from PyQt4.QtGui import QStyleOptionTabBarBase
        from PyQt4.QtGui import QStyleOptionTabWidgetFrame
        from PyQt4.QtGui import QStyleOptionTitleBar
        from PyQt4.QtGui import QStyleOptionToolBar
        from PyQt4.QtGui import QStyleOptionToolBox
        from PyQt4.QtGui import QStyleOptionToolButton
        from PyQt4.QtGui import QStyleOptionViewItem
        from PyQt4.QtGui import QStylePainter
        from PyQt4.QtGui import QStyledItemDelegate
        from PyQt4.QtGui import QSwipeGesture
        from PyQt4.QtGui import QSystemTrayIcon
        from PyQt4.QtGui import QTabBar
        from PyQt4.QtGui import QTabWidget
        from PyQt4.QtGui import QTableView
        from PyQt4.QtGui import QTableWidget
        from PyQt4.QtGui import QTableWidgetItem
        from PyQt4.QtGui import QTableWidgetSelectionRange
        from PyQt4.QtGui import QTapAndHoldGesture
        from PyQt4.QtGui import QTapGesture
        from PyQt4.QtGui import QTextBrowser
        from PyQt4.QtGui import QTextEdit
        from PyQt4.QtGui import QTimeEdit
        from PyQt4.QtGui import QToolBar
        from PyQt4.QtGui import QToolBox
        from PyQt4.QtGui import QToolButton
        from PyQt4.QtGui import QToolTip
        from PyQt4.QtGui import QTreeView
        from PyQt4.QtGui import QTreeWidget
        from PyQt4.QtGui import QTreeWidgetItem
        from PyQt4.QtGui import QTreeWidgetItemIterator
        from PyQt4.QtGui import QUndoCommand
        from PyQt4.QtGui import QUndoGroup
        from PyQt4.QtGui import QUndoStack
        from PyQt4.QtGui import QUndoView
        from PyQt4.QtGui import QVBoxLayout
        from PyQt4.QtGui import QWhatsThis
        from PyQt4.QtGui import QWidget
        from PyQt4.QtGui import QWidgetAction
        from PyQt4.QtGui import QWidgetItem
        from PyQt4.QtGui import QWizard
        from PyQt4.QtGui import QWizardPage
        from PyQt4.QtGui import qApp
        from PyQt4.QtGui import qDrawBorderPixmap
        from PyQt4.QtGui import qDrawPlainRect
        from PyQt4.QtGui import qDrawShadeLine
        from PyQt4.QtGui import qDrawShadePanel
        from PyQt4.QtGui import qDrawShadeRect
        from PyQt4.QtGui import qDrawWinButton
        from PyQt4.QtGui import qDrawWinPanel
        from PyQt4.QtGui import QFileDialog as OldFileDialog

        class QFileDialog(OldFileDialog):
            @staticmethod
            def getOpenFileName(parent=None, caption='', directory='', filter='',
                                selectedFilter='',
                                options=OldFileDialog.Options()):
                return OldFileDialog.getOpenFileNameAndFilter(
                    parent, caption, directory, filter, selectedFilter, options)

            @staticmethod
            def getOpenFileNames(parent=None, caption='', directory='', filter='',
                                 selectedFilter='',
                                 options=OldFileDialog.Options()):
                return OldFileDialog.getOpenFileNamesAndFilter(
                    parent, caption, directory, filter, selectedFilter, options)

            @staticmethod
            def getSaveFileName(parent=None, caption='', directory='', filter='',
                                selectedFilter='',
                                options=OldFileDialog.Options()):
                return OldFileDialog.getSaveFileNameAndFilter(
                    parent, caption, directory, filter, selectedFilter, options)

    elif os.environ[QT_API] == PYSIDE_API:
        from PySide.QtGui import QAbstractButton
        from PySide.QtGui import QAbstractGraphicsShapeItem
        from PySide.QtGui import QAbstractItemDelegate
        from PySide.QtGui import QAbstractItemView
        from PySide.QtGui import QAbstractScrollArea
        from PySide.QtGui import QAbstractSlider
        from PySide.QtGui import QAbstractSpinBox
        from PySide.QtGui import QAction
        from PySide.QtGui import QActionGroup
        from PySide.QtGui import QApplication
        from PySide.QtGui import QBoxLayout
        from PySide.QtGui import QButtonGroup
        from PySide.QtGui import QCalendarWidget
        from PySide.QtGui import QCheckBox
        from PySide.QtGui import QColorDialog
        from PySide.QtGui import QColumnView
        from PySide.QtGui import QComboBox
        from PySide.QtGui import QCommandLinkButton
        from PySide.QtGui import QCommonStyle
        from PySide.QtGui import QCompleter
        from PySide.QtGui import QDataWidgetMapper
        from PySide.QtGui import QDateEdit
        from PySide.QtGui import QDateTimeEdit
        from PySide.QtGui import QDesktopWidget
        from PySide.QtGui import QDial
        from PySide.QtGui import QDialog
        from PySide.QtGui import QDialogButtonBox
        from PySide.QtGui import QDirModel
        from PySide.QtGui import QDockWidget
        from PySide.QtGui import QDoubleSpinBox
        from PySide.QtGui import QErrorMessage
        from PySide.QtGui import QFileIconProvider
        from PySide.QtGui import QFileSystemModel
        from PySide.QtGui import QFocusFrame
        from PySide.QtGui import QFontComboBox
        from PySide.QtGui import QFontDialog
        from PySide.QtGui import QFormLayout
        from PySide.QtGui import QFrame
        from PySide.QtGui import QGesture
        from PySide.QtGui import QGestureEvent
        from PySide.QtGui import QGestureRecognizer
        from PySide.QtGui import QGraphicsAnchor
        from PySide.QtGui import QGraphicsAnchorLayout
        from PySide.QtGui import QGraphicsBlurEffect
        from PySide.QtGui import QGraphicsColorizeEffect
        from PySide.QtGui import QGraphicsDropShadowEffect
        from PySide.QtGui import QGraphicsEffect
        from PySide.QtGui import QGraphicsEllipseItem
        from PySide.QtGui import QGraphicsGridLayout
        from PySide.QtGui import QGraphicsItem
        from PySide.QtGui import QGraphicsItemGroup
        from PySide.QtGui import QGraphicsLayout
        from PySide.QtGui import QGraphicsLayoutItem
        from PySide.QtGui import QGraphicsLineItem
        from PySide.QtGui import QGraphicsLinearLayout
        from PySide.QtGui import QGraphicsObject
        from PySide.QtGui import QGraphicsOpacityEffect
        from PySide.QtGui import QGraphicsPathItem
        from PySide.QtGui import QGraphicsPixmapItem
        from PySide.QtGui import QGraphicsPolygonItem
        from PySide.QtGui import QGraphicsProxyWidget
        from PySide.QtGui import QGraphicsRectItem
        from PySide.QtGui import QGraphicsRotation
        from PySide.QtGui import QGraphicsScale
        from PySide.QtGui import QGraphicsScene
        from PySide.QtGui import QGraphicsSceneContextMenuEvent
        from PySide.QtGui import QGraphicsSceneDragDropEvent
        from PySide.QtGui import QGraphicsSceneEvent
        from PySide.QtGui import QGraphicsSceneHelpEvent
        from PySide.QtGui import QGraphicsSceneHoverEvent
        from PySide.QtGui import QGraphicsSceneMouseEvent
        from PySide.QtGui import QGraphicsSceneMoveEvent
        from PySide.QtGui import QGraphicsSceneResizeEvent
        from PySide.QtGui import QGraphicsSceneWheelEvent
        from PySide.QtGui import QGraphicsSimpleTextItem
        from PySide.QtGui import QGraphicsTextItem
        from PySide.QtGui import QGraphicsTransform
        from PySide.QtGui import QGraphicsView
        from PySide.QtGui import QGraphicsWidget
        from PySide.QtGui import QGridLayout
        from PySide.QtGui import QGroupBox
        from PySide.QtGui import QHBoxLayout
        from PySide.QtGui import QHeaderView
        from PySide.QtGui import QInputDialog
        from PySide.QtGui import QItemDelegate
        from PySide.QtGui import QItemEditorCreatorBase
        from PySide.QtGui import QItemEditorFactory
        from PySide.QtGui import QKeyEventTransition
        from PySide.QtGui import QLCDNumber
        from PySide.QtGui import QLabel
        from PySide.QtGui import QLayout
        from PySide.QtGui import QLayoutItem
        from PySide.QtGui import QLineEdit
        from PySide.QtGui import QListView
        from PySide.QtGui import QListWidget
        from PySide.QtGui import QListWidgetItem
        from PySide.QtGui import QMainWindow
        from PySide.QtGui import QMdiArea
        from PySide.QtGui import QMdiSubWindow
        from PySide.QtGui import QMenu
        from PySide.QtGui import QMenuBar
        from PySide.QtGui import QMessageBox
        from PySide.QtGui import QMouseEventTransition
        from PySide.QtGui import QPanGesture
        from PySide.QtGui import QPinchGesture
        from PySide.QtGui import QPlainTextDocumentLayout
        from PySide.QtGui import QPlainTextEdit
        from PySide.QtGui import QProgressBar
        from PySide.QtGui import QProgressDialog
        from PySide.QtGui import QPushButton
        from PySide.QtGui import QRadioButton
        from PySide.QtGui import QRubberBand
        from PySide.QtGui import QScrollArea
        from PySide.QtGui import QScrollBar
        from PySide.QtGui import QShortcut
        from PySide.QtGui import QSizeGrip
        from PySide.QtGui import QSizePolicy
        from PySide.QtGui import QSlider
        from PySide.QtGui import QSpacerItem
        from PySide.QtGui import QSpinBox
        from PySide.QtGui import QSplashScreen
        from PySide.QtGui import QSplitter
        from PySide.QtGui import QSplitterHandle
        from PySide.QtGui import QStackedLayout
        from PySide.QtGui import QStackedWidget
        from PySide.QtGui import QStatusBar
        from PySide.QtGui import QStyle
        from PySide.QtGui import QStyleFactory
        from PySide.QtGui import QStyleHintReturn
        from PySide.QtGui import QStyleHintReturnMask
        from PySide.QtGui import QStyleHintReturnVariant
        from PySide.QtGui import QStyleOption
        from PySide.QtGui import QStyleOptionButton
        from PySide.QtGui import QStyleOptionComboBox
        from PySide.QtGui import QStyleOptionComplex
        from PySide.QtGui import QStyleOptionDockWidget
        from PySide.QtGui import QStyleOptionFocusRect
        from PySide.QtGui import QStyleOptionFrame
        from PySide.QtGui import QStyleOptionGraphicsItem
        from PySide.QtGui import QStyleOptionGroupBox
        from PySide.QtGui import QStyleOptionHeader
        from PySide.QtGui import QStyleOptionMenuItem
        from PySide.QtGui import QStyleOptionProgressBar
        from PySide.QtGui import QStyleOptionRubberBand
        from PySide.QtGui import QStyleOptionSizeGrip
        from PySide.QtGui import QStyleOptionSlider
        from PySide.QtGui import QStyleOptionSpinBox
        from PySide.QtGui import QStyleOptionTab
        from PySide.QtGui import QStyleOptionTabBarBase
        from PySide.QtGui import QStyleOptionTabWidgetFrame
        from PySide.QtGui import QStyleOptionTitleBar
        from PySide.QtGui import QStyleOptionToolBar
        from PySide.QtGui import QStyleOptionToolBox
        from PySide.QtGui import QStyleOptionToolButton
        from PySide.QtGui import QStyleOptionViewItem
        from PySide.QtGui import QStylePainter
        from PySide.QtGui import QStyledItemDelegate
        from PySide.QtGui import QSwipeGesture
        from PySide.QtGui import QSystemTrayIcon
        from PySide.QtGui import QTabBar
        from PySide.QtGui import QTabWidget
        from PySide.QtGui import QTableView
        from PySide.QtGui import QTableWidget
        from PySide.QtGui import QTableWidgetItem
        from PySide.QtGui import QTableWidgetSelectionRange
        from PySide.QtGui import QTapAndHoldGesture
        from PySide.QtGui import QTapGesture
        from PySide.QtGui import QTextBrowser
        from PySide.QtGui import QTextEdit
        from PySide.QtGui import QTimeEdit
        from PySide.QtGui import QToolBar
        from PySide.QtGui import QToolBox
        from PySide.QtGui import QToolButton
        from PySide.QtGui import QToolTip
        from PySide.QtGui import QTreeView
        from PySide.QtGui import QTreeWidget
        from PySide.QtGui import QTreeWidgetItem
        from PySide.QtGui import QTreeWidgetItemIterator
        from PySide.QtGui import QUndoCommand
        from PySide.QtGui import QUndoGroup
        from PySide.QtGui import QUndoStack
        from PySide.QtGui import QUndoView
        from PySide.QtGui import QVBoxLayout
        from PySide.QtGui import QWhatsThis
        from PySide.QtGui import QWidget
        from PySide.QtGui import QWidgetAction
        from PySide.QtGui import QWidgetItem
        from PySide.QtGui import QWizard
        from PySide.QtGui import QWizardPage
        from PySide.QtGui import qApp
        from PySide.QtGui import QFileDialog
except ImportError:
    # allowed when building doc with sphinx (e.g. on readthedocs)
    assert os.environ.get('SPHINX', None) == '1'

    class QColor(object):
        def __init__(self, *args, **kwargs):
            pass

    class QTextEdit(object):
        class ExtraSelection(object):
            pass

    class QPlainTextEdit(object):
        pass

    class QPaintEvent(object):
        pass

    class QKeyEvent(object):
        pass

    class QMouseEvent(object):
        pass

    class QWheelEvent(object):
        pass

    class QFocusEvent(object):
        pass

    class QWidget(object):
        pass

    class QTextBlockUserData(object):
        pass

    class QSyntaxHighlighter(object):
        pass

    class QTextCursor(object):
        pass

    class QTextBlock(object):
        pass

    class QTextDocument(object):
        pass

    class QTextCharFormat(object):
        pass

    class QFont(object):
        pass

    class QTableWidget(object):
        pass

    class QIcon(object):
        pass

    class Foo(object):
        pass

    class QTextEdit(object):
        ExtraSelection = Foo
        pass

    class QColor(object):
        def __init__(self, *args, **kwargs):
            pass

    class QDialog(object):
        pass

    class QTabBar(object):
        pass

    class QTabWidget:
        pass

    class QMenu:
        pass

    class QAction:
        pass