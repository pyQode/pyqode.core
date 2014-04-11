# -*- coding: utf-8 -*-
"""
Server used for tests
"""
import sys
import os
# ensure sys knows about pyqode.core in the test env
sys.path.insert(0, os.path.abspath('..'))
from pyqode.core.server_api import server
from pyqode.core.server_api import workers


if __name__ == '__main__':
    workers.CodeCompletionWorker.providers.append(
        workers.DocumentWordsProvider())
    server.run()
