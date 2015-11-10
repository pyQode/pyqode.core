import sys
from pyqode.core.widgets import InteractiveConsole


def test_console():
    ic = InteractiveConsole()
    if sys.platform == 'win32':
        ic.start_process('dir')
    else:
        ic.start_process('ls')
    ic.process.waitForFinished()
    assert ic.process.exitStatus() == 0
