#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Server used for tests
"""
import sys
import os
# ensure sys knows about pyqode.core in the test env
sys.path.insert(0, os.path.abspath('..'))
from pyqode.core import backend


if __name__ == '__main__':
    print('Server started')
    backend.CodeCompletionWorker.providers.append(
        backend.DocumentWordsProvider())
    backend.serve_forever()
