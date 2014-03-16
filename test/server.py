"""
Server used for tests
"""
from pyqode.core.api import code_completion
from pyqode.core.api import server
from pyqode.core.api import workers

if __name__ == '__main__':
    workers.CodeCompletion.providers.append(
        code_completion.DocumentWordsProvider())
    server.run()
