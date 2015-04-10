#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Server used for tests
"""
import sys
import os
# ensure sys knows about pyqode.core in the test env
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
try:
    from pyqode.core import backend
except ImportError:
    print('Failed to import backend', sys.stderr)
    print('sys.path = %r' % sys.path, sys.stderr)


if __name__ == '__main__':
    print('Server started')
    print(sys.path)
    print(os.getcwd(), sys.stderr)
    backend.CodeCompletionWorker.providers.append(
        backend.DocumentWordsProvider())
    backend.serve_forever()
