# -*- coding: utf-8 -*-
"""
This scripts configures the test suite. We do two things:

    - setup the logging module
    - create ONE SINGLE INSTANCE of QApplication:
      this implies that you must use **QApplication.instance** in your
      test scripts.
"""
import logging
logging.basicConfig(level=logging.INFO)
import pytest
from PyQt4.QtGui import QApplication
import sys


app = None


@pytest.fixture(scope="session", autouse=True)
def create_qapplication(request):
    global app
    print('create qapplication')
    app = QApplication(sys.argv)

    def teardown():
        global app
        print("teardown qapplication")
        app = None
        del app

    request.addfinalizer(teardown)
