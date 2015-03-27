# -*- coding: utf-8 -*-
"""
This scripts configures the test suite. We do two things:

    - setup the logging module
    - create ONE SINGLE INSTANCE of QApplication:
      this implies that you must use **QApplication.instance** in your
      test scripts.
"""
import os
import logging
import pytest
import sys

os.environ['PYQODE_CORE_TESTSUITE'] = '1'


# -------------------
# Setup runtest
# -------------------
def pytest_runtest_setup(item):
    """
    Display test method name in active window title bar
    ;param item: test item to run
    """
    from pyqode.qt.QtWidgets import QApplication
    global EDITOR, APP
    if APP is None:
        APP = QApplication(sys.argv)
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
APP = None
EDITOR = None


# -------------------
# Session fixtures
# -------------------
@pytest.fixture(scope="session", autouse=True)
def start_app(request):
    """
    Start application and create the test code editor widget.
    """
    from pyqode.core.api.code_edit import CodeEdit
    from pyqode.core.backend import server
    from test.helpers import setup_editor, wait_for_connected
    global APP, EDITOR
    logging.info('setup session editor')
    EDITOR = CodeEdit()
    setup_editor(EDITOR)
    EDITOR.backend.start(server.__file__)
    wait_for_connected(EDITOR)

    def fin():
        """
        Finalize fixture, stop backend and delete editor widget.
        """
        global EDITOR, APP
        logging.info('teardown session editor')
        EDITOR.close()
        EDITOR.delete()
        APP.quit()
        del EDITOR
        del APP

    request.addfinalizer(fin)


@pytest.fixture()
def editor(request):
    """
    Editor fixture, returns a reference to the test editor widget with all
    parameters automatically reset to "factory defaults".
    """
    from test.helpers import reset_editor
    global EDITOR
    reset_editor(EDITOR)
    return EDITOR
