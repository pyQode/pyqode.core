import logging
logging.basicConfig(level=logging.INFO)
import pytest
from PyQt4.QtGui import QApplication
import sys


app = None


@pytest.fixture(scope="session", autouse=True)
def create_qapplication(request):
    global app
    app = QApplication(sys.argv)

    def teardown():
        global app
        print("teardown qapplication")
        app = None
        del app

    request.addfinalizer(teardown)
