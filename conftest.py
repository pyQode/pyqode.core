# -*- coding: utf-8 -*-
"""
This scripts configures the test suite. We do two things:

    - setup the logging module
    - create ONE SINGLE INSTANCE of QApplication:
      this implies that you must use **QApplication.instance** in your
      test scripts.
"""
import sys
from PyQt4.QtGui import QApplication

# 1. setup logging
import logging
logging.basicConfig(level=logging.DEBUG)

# 2. create qt application
app = QApplication(sys.argv)
