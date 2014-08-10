import os
from pyqode.core.qt import QT_API
from pyqode.core.qt import PYQT5_API
from pyqode.core.qt import PYQT4_API
from pyqode.core.qt import PYSIDE_API

try:
    if os.environ[QT_API] == PYQT5_API:
        from PyQt5.QtCore import *
        from PyQt5.Qt import Qt
        from PyQt5.QtCore import pyqtSignal as Signal
        from PyQt5.QtCore import pyqtSlot as Slot
        from PyQt5.QtCore import pyqtProperty as Property
        from PyQt5.QtCore import pyqtProperty as Property
        from PyQt5.QtCore import QT_VERSION_STR as __version__
    elif os.environ[QT_API] == PYQT4_API:
        from PyQt4.QtCore import *
        from PyQt4.Qt import Qt
        from PyQt4.QtCore import pyqtSignal as Signal
        from PyQt4.QtCore import pyqtSlot as Slot
        from PyQt4.QtCore import pyqtProperty as Property
        from PyQt4.QtCore import pyqtProperty as Property
        from PyQt4.QtCore import QT_VERSION_STR as __version__
    elif os.environ[QT_API] == PYSIDE_API:
        from PySide.QtCore import *
        import PySide.QtCore
        __version__ = PySide.QtCore.__version__
        from PySide.QtCore import *
except ImportError:
    # allowed when building doc with sphinx (on readthedocs)
    assert os.environ.get('SPHINX', None) == '1'

    class Qt(object):
        blue = None
        red = None

    class QObject(object):
        pass

    class Signal(object):
        def __init__(self, *args):
            pass

    def Slot(*types):
        def decorator(func):
            import functools

            @functools.wraps(func)
            def wrapper(*args, **kwds):
                return func(*args, **kwds)
            return wrapper
        return decorator

    class QThread(object):
        pass

    class QEvent(object):
        @staticmethod
        def Type(foo):
            pass

        @staticmethod
        def registerEventType():
            pass

    def qRegisterResourceData(*args):
        pass

    class QRegExp(object):
        pass

    class Property(object):
        def __init__(self, *args, **kwargs):
            pass

    class QProcess:
        pass
