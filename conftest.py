# -*- coding: utf-8 -*-
"""
This scripts configures the test suite. We do two things:

    - setup the logging module
    - create ONE SINGLE INSTANCE of QApplication:
      this implies that you must use **QApplication.instance** in your
      test scripts.
"""
import pytest
from PyQt4.QtGui import QApplication
import sys

# 1. setup logging
import logging
logging.basicConfig(level=logging.INFO)

# 2. create qt application
app = QApplication(sys.argv)


# def teardown():
#     global app
#     app = None
#     del app
#
#
# @pytest.fixture(scope="session", autouse=True)
# def create_qapplication(request):
#     request.addfinalizer(teardown)
