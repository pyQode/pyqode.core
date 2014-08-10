# -*- coding: utf-8 -*-
"""
This scripts configures the test suite. We do two things:

    - setup the logging module
    - create ONE SINGLE INSTANCE of QApplication:
      this implies that you must use **QApplication.instance** in your
      test scripts.
"""
import logging
import os
import sys
import pytest
import time
from pyqode.core.api.code_edit import CodeEdit

try:
    import faulthandler
    faulthandler.enable()
except ImportError:
    pass


# -------------------
# Setup runtest
# -------------------
def pytest_runtest_setup(item):
    """
    Skips tesks marker with a ``skip_on_travis`` marker.
    """
    if isinstance(item, item.Function):
        travis_platform = True if 'TRAVIS' in os.environ else False
        if travis_platform and item.get_marker('skip_on_travis'):
            pytest.skip("test skipped when ran on Travis-CI: %r" % item)
        else:
            logging.info("------------------- %s -------------------",
                         item)


# -------------------
# Setup logging
# -------------------
logging.basicConfig(level=logging.DEBUG,
                    filename='pytest.log',
                    filemode='w')

# -------------------
# Setup QApplication
# -------------------
# 2. create qt application
from pyqode.qt.QtWidgets import QApplication
_app = QApplication(sys.argv)
_widget = None


# -------------------
# Session fixtures
# -------------------
@pytest.fixture(scope="session")
def app(request):
    global _app
    return app


@pytest.fixture(scope="session")
def editor(request):
    global _app, _widget
    from test import helpers

    logging.info('setup session editor')

    _widget = CodeEdit()
    _widget.backend.start(helpers.server_path())
    helpers.wait_for_connected(_widget)
    helpers.setup_editor(_widget)
    _widget.show()
    _widget.resize(800, 600)
    _app.setActiveWindow(_widget)
    _widget.save_on_focus_out = False

    def fin():
        global _widget
        logging.info('teardown session editor')
        _widget.backend.stop()
        del _widget

    request.addfinalizer(fin)

    return _widget
