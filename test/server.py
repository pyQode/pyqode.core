# -*- coding: utf-8 -*-
"""
Server used for tests
"""
import sys
import os
# ensure sys knows about pyqode.core in the test env
sys.path.insert(0, os.path.abspath('..'))
from pyqode.core import server_api


if __name__ == '__main__':
    server_api.CodeCompletionWorker.providers.append(
        server_api.DocumentWordsProvider())
    server_api.run()
