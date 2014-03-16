"""
Server used for tests
"""
import sys
import os
# ensure sys knows about pyqode.core
sys.path.insert(0, os.path.abspath('..'))
from pyqode.core import code_completion
from pyqode.core import server
from pyqode.core import workers

if __name__ == '__main__':
    workers.CodeCompletion.providers.append(
        code_completion.DocumentWordsProvider())
    server.run()
