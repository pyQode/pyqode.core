import logging
logging.basicConfig(level=logging.INFO)
import os
os.environ['QT_API'] = 'PyQt5'
from pyqode.qt import QtCore, QtGui, QtWidgets
print('Qt version:%s' % QtCore.__version__)
print(QtCore.QEvent)
print(QtGui.QPainter)
print(QtWidgets.QWidget)

