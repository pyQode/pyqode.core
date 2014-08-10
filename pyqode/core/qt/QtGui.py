import os
from pyqode.core.qt import QT_API
from pyqode.core.qt import PYQT5_API
from pyqode.core.qt import PYQT4_API
from pyqode.core.qt import PYSIDE_API

try:
    if os.environ[QT_API] == PYQT5_API:
        from PyQt5.QtGui import *
    elif os.environ[QT_API] == PYQT4_API:
        from PyQt4.QtGui import QAbstractTextDocumentLayout
        from PyQt4.QtGui import QActionEvent
        from PyQt4.QtGui import QBitmap
        from PyQt4.QtGui import QBrush
        from PyQt4.QtGui import QClipboard
        from PyQt4.QtGui import QCloseEvent
        from PyQt4.QtGui import QColor
        from PyQt4.QtGui import QConicalGradient
        from PyQt4.QtGui import QContextMenuEvent
        from PyQt4.QtGui import QCursor
        from PyQt4.QtGui import QDesktopServices
        from PyQt4.QtGui import QDoubleValidator
        from PyQt4.QtGui import QDrag
        from PyQt4.QtGui import QDragEnterEvent
        from PyQt4.QtGui import QDragLeaveEvent
        from PyQt4.QtGui import QDragMoveEvent
        from PyQt4.QtGui import QDropEvent
        from PyQt4.QtGui import QFileOpenEvent
        from PyQt4.QtGui import QFocusEvent
        from PyQt4.QtGui import QFont
        from PyQt4.QtGui import QFontDatabase
        from PyQt4.QtGui import QFontInfo
        from PyQt4.QtGui import QFontMetrics
        from PyQt4.QtGui import QFontMetricsF
        from PyQt4.QtGui import QGlyphRun
        from PyQt4.QtGui import QGradient
        from PyQt4.QtGui import QHelpEvent
        from PyQt4.QtGui import QHideEvent
        from PyQt4.QtGui import QHoverEvent
        from PyQt4.QtGui import QIcon
        from PyQt4.QtGui import QIconDragEvent
        from PyQt4.QtGui import QIconEngine
        from PyQt4.QtGui import QImage
        from PyQt4.QtGui import QImageIOHandler
        from PyQt4.QtGui import QImageReader
        from PyQt4.QtGui import QImageWriter
        from PyQt4.QtGui import QInputEvent
        from PyQt4.QtGui import QIntValidator
        from PyQt4.QtGui import QKeyEvent
        from PyQt4.QtGui import QKeySequence
        from PyQt4.QtGui import QLinearGradient
        from PyQt4.QtGui import QMatrix2x2
        from PyQt4.QtGui import QMatrix2x3
        from PyQt4.QtGui import QMatrix2x4
        from PyQt4.QtGui import QMatrix3x2
        from PyQt4.QtGui import QMatrix3x3
        from PyQt4.QtGui import QMatrix3x4
        from PyQt4.QtGui import QMatrix4x2
        from PyQt4.QtGui import QMatrix4x3
        from PyQt4.QtGui import QMatrix4x4
        from PyQt4.QtGui import QMouseEvent
        from PyQt4.QtGui import QMoveEvent
        from PyQt4.QtGui import QMovie
        from PyQt4.QtGui import QPaintDevice
        from PyQt4.QtGui import QPaintEngine
        from PyQt4.QtGui import QPaintEngineState
        from PyQt4.QtGui import QPaintEvent
        from PyQt4.QtGui import QPainter
        from PyQt4.QtGui import QPainterPath
        from PyQt4.QtGui import QPainterPathStroker
        from PyQt4.QtGui import QPalette
        from PyQt4.QtGui import QPen
        from PyQt4.QtGui import QPicture
        from PyQt4.QtGui import QPictureIO
        from PyQt4.QtGui import QPixmap
        from PyQt4.QtGui import QPixmapCache
        from PyQt4.QtGui import QPolygon
        from PyQt4.QtGui import QPolygonF
        from PyQt4.QtGui import QQuaternion
        from PyQt4.QtGui import QRadialGradient
        from PyQt4.QtGui import QRawFont
        from PyQt4.QtGui import QRegExpValidator
        from PyQt4.QtGui import QRegion
        from PyQt4.QtGui import QResizeEvent
        from PyQt4.QtGui import QSessionManager
        from PyQt4.QtGui import QShortcutEvent
        from PyQt4.QtGui import QShowEvent
        from PyQt4.QtGui import QStandardItem
        from PyQt4.QtGui import QStandardItemModel
        from PyQt4.QtGui import QStaticText
        from PyQt4.QtGui import QStatusTipEvent
        from PyQt4.QtGui import QSyntaxHighlighter
        from PyQt4.QtGui import QSortFilterProxyModel
        from PyQt4.QtGui import QTabletEvent
        from PyQt4.QtGui import QTextBlock
        from PyQt4.QtGui import QTextBlockFormat
        from PyQt4.QtGui import QTextBlockGroup
        from PyQt4.QtGui import QTextBlockUserData
        from PyQt4.QtGui import QTextCharFormat
        from PyQt4.QtGui import QTextCursor
        from PyQt4.QtGui import QTextDocument
        from PyQt4.QtGui import QTextDocumentFragment
        from PyQt4.QtGui import QTextDocumentWriter
        from PyQt4.QtGui import QTextFormat
        from PyQt4.QtGui import QTextFragment
        from PyQt4.QtGui import QTextFrame
        from PyQt4.QtGui import QTextFrameFormat
        from PyQt4.QtGui import QTextImageFormat
        from PyQt4.QtGui import QTextInlineObject
        from PyQt4.QtGui import QTextItem
        from PyQt4.QtGui import QTextLayout
        from PyQt4.QtGui import QTextLength
        from PyQt4.QtGui import QTextLine
        from PyQt4.QtGui import QTextList
        from PyQt4.QtGui import QTextListFormat
        from PyQt4.QtGui import QTextObject
        from PyQt4.QtGui import QTextObjectInterface
        from PyQt4.QtGui import QTextOption
        from PyQt4.QtGui import QTextTable
        from PyQt4.QtGui import QTextTableCell
        from PyQt4.QtGui import QTextTableCellFormat
        from PyQt4.QtGui import QTextTableFormat
        from PyQt4.QtGui import QTouchEvent
        from PyQt4.QtGui import QTransform
        from PyQt4.QtGui import QValidator
        from PyQt4.QtGui import QVector2D
        from PyQt4.QtGui import QVector3D
        from PyQt4.QtGui import QVector4D
        from PyQt4.QtGui import QWhatsThisClickedEvent
        from PyQt4.QtGui import QWheelEvent
        from PyQt4.QtGui import QWindowStateChangeEvent
        from PyQt4.QtGui import qAlpha
        from PyQt4.QtGui import qBlue
        from PyQt4.QtGui import qFuzzyCompare
        from PyQt4.QtGui import qGray
        from PyQt4.QtGui import qGreen
        from PyQt4.QtGui import qIsGray
        from PyQt4.QtGui import qRed
        from PyQt4.QtGui import qRgb
        from PyQt4.QtGui import qRgba
        from PyQt4.QtGui import QStyleOptionViewItemV2
    elif os.environ[QT_API] == PYSIDE_API:
        from PySide.QtGui import QAbstractTextDocumentLayout
        from PySide.QtGui import QActionEvent
        from PySide.QtGui import QBitmap
        from PySide.QtGui import QBrush
        from PySide.QtGui import QClipboard
        from PySide.QtGui import QCloseEvent
        from PySide.QtGui import QColor
        from PySide.QtGui import QConicalGradient
        from PySide.QtGui import QContextMenuEvent
        from PySide.QtGui import QCursor
        from PySide.QtGui import QDesktopServices
        from PySide.QtGui import QDoubleValidator
        from PySide.QtGui import QDrag
        from PySide.QtGui import QDragEnterEvent
        from PySide.QtGui import QDragLeaveEvent
        from PySide.QtGui import QDragMoveEvent
        from PySide.QtGui import QDropEvent
        from PySide.QtGui import QFileOpenEvent
        from PySide.QtGui import QFocusEvent
        from PySide.QtGui import QFont
        from PySide.QtGui import QFontDatabase
        from PySide.QtGui import QFontInfo
        from PySide.QtGui import QFontMetrics
        from PySide.QtGui import QFontMetricsF
        from PySide.QtGui import QGradient
        from PySide.QtGui import QHelpEvent
        from PySide.QtGui import QHideEvent
        from PySide.QtGui import QHoverEvent
        from PySide.QtGui import QIcon
        from PySide.QtGui import QIconDragEvent
        from PySide.QtGui import QIconEngine
        from PySide.QtGui import QImage
        from PySide.QtGui import QImageIOHandler
        from PySide.QtGui import QImageReader
        from PySide.QtGui import QImageWriter
        from PySide.QtGui import QInputEvent
        from PySide.QtGui import QIntValidator
        from PySide.QtGui import QKeyEvent
        from PySide.QtGui import QKeySequence
        from PySide.QtGui import QLinearGradient
        from PySide.QtGui import QMatrix2x2
        from PySide.QtGui import QMatrix2x3
        from PySide.QtGui import QMatrix2x4
        from PySide.QtGui import QMatrix3x2
        from PySide.QtGui import QMatrix3x3
        from PySide.QtGui import QMatrix3x4
        from PySide.QtGui import QMatrix4x2
        from PySide.QtGui import QMatrix4x3
        from PySide.QtGui import QMatrix4x4
        from PySide.QtGui import QMouseEvent
        from PySide.QtGui import QMoveEvent
        from PySide.QtGui import QMovie
        from PySide.QtGui import QPaintDevice
        from PySide.QtGui import QPaintEngine
        from PySide.QtGui import QPaintEngineState
        from PySide.QtGui import QPaintEvent
        from PySide.QtGui import QPainter
        from PySide.QtGui import QPainterPath
        from PySide.QtGui import QPainterPathStroker
        from PySide.QtGui import QPalette
        from PySide.QtGui import QPen
        from PySide.QtGui import QPicture
        from PySide.QtGui import QPictureIO
        from PySide.QtGui import QPixmap
        from PySide.QtGui import QPixmapCache
        from PySide.QtGui import QPolygon
        from PySide.QtGui import QPolygonF
        from PySide.QtGui import QQuaternion
        from PySide.QtGui import QRadialGradient
        from PySide.QtGui import QRegExpValidator
        from PySide.QtGui import QRegion
        from PySide.QtGui import QResizeEvent
        from PySide.QtGui import QSessionManager
        from PySide.QtGui import QShortcutEvent
        from PySide.QtGui import QShowEvent
        from PySide.QtGui import QStandardItem
        from PySide.QtGui import QStandardItemModel
        from PySide.QtGui import QStatusTipEvent
        from PySide.QtGui import QSyntaxHighlighter
        from PySide.QtGui import QSortFilterProxyModel
        from PySide.QtGui import QTabletEvent
        from PySide.QtGui import QTextBlock
        from PySide.QtGui import QTextBlockFormat
        from PySide.QtGui import QTextBlockGroup
        from PySide.QtGui import QTextBlockUserData
        from PySide.QtGui import QTextCharFormat
        from PySide.QtGui import QTextCursor
        from PySide.QtGui import QTextDocument
        from PySide.QtGui import QTextDocumentFragment
        from PySide.QtGui import QTextFormat
        from PySide.QtGui import QTextFragment
        from PySide.QtGui import QTextFrame
        from PySide.QtGui import QTextFrameFormat
        from PySide.QtGui import QTextImageFormat
        from PySide.QtGui import QTextInlineObject
        from PySide.QtGui import QTextItem
        from PySide.QtGui import QTextLayout
        from PySide.QtGui import QTextLength
        from PySide.QtGui import QTextLine
        from PySide.QtGui import QTextList
        from PySide.QtGui import QTextListFormat
        from PySide.QtGui import QTextObject
        from PySide.QtGui import QTextObjectInterface
        from PySide.QtGui import QTextOption
        from PySide.QtGui import QTextTable
        from PySide.QtGui import QTextTableCell
        from PySide.QtGui import QTextTableCellFormat
        from PySide.QtGui import QTextTableFormat
        from PySide.QtGui import QTouchEvent
        from PySide.QtGui import QTransform
        from PySide.QtGui import QValidator
        from PySide.QtGui import QVector2D
        from PySide.QtGui import QVector3D
        from PySide.QtGui import QVector4D
        from PySide.QtGui import QWhatsThisClickedEvent
        from PySide.QtGui import QWheelEvent
        from PySide.QtGui import QWindowStateChangeEvent
        from PySide.QtGui import QStyleOptionViewItemV2
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
