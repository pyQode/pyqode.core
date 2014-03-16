"""
Server used for tests
"""
from pyqode.core import code_completion
from pyqode.core import server
from pyqode.core import workers

if __name__ == '__main__':
    workers.CodeCompletion.providers.append(
        code_completion.DocumentWordsProvider())
    server.run()
