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
try:
    import faulthandler
    faulthandler.enable()
except ImportError:
    pass
import pytest
from pyqode.core.api.code_edit import CodeEdit


# -------------------
# Setup runtest
# -------------------
def pytest_runtest_setup(item):
    """
    Display test method name in active window title bar
    ;param item: test item to run
    """
    global _widget
    module, line, method = item.location
    module = module.replace('.py', '.')
    title = module + method
    widgets = QApplication.instance().topLevelWidgets()
    for w in widgets:
        w.setWindowTitle(title)
    logging.info("------------------- %s -------------------", title)


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
    """
    Application fixture, returns a reference to the main QApplication.
    :param request:
    :return:
    """
    global _app
    return app


@pytest.fixture(scope="session")
def editor(request):
    """
    Editor fixture, returns a reference to the test editor widget.
    :param request: fixture request
    """
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
        """
        Finalize fixture, stop backend and delete editor widget.
        """
        global _widget
        logging.info('teardown session editor')
        _widget.backend.stop()
        del _widget

    request.addfinalizer(fin)

    return _widget
