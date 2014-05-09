# -*- coding: utf-8 -*-
"""
This scripts configures the test suite. We do two things:

    - setup the logging module
    - create ONE SINGLE INSTANCE of QApplication:
      this implies that you must use **QApplication.instance** in your
      test scripts.
"""
import os
import sys
import pytest

from PyQt4.QtGui import QApplication

# 1. setup logging
import logging
logging.basicConfig(level=logging.DEBUG)

# 2. create qt application
app = QApplication(sys.argv)


def pytest_runtest_setup(item):
    if isinstance(item, item.Function):
        travis_platform = True if 'TRAVIS' in os.environ else False
        if travis_platform and item.get_marker('skip_on_travis'):
            pytest.skip("test skipped when ran on Travis-CI: %r" % item)
