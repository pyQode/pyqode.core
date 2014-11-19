#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Simple server which adds a DocumentWordsProvider to the CodeCompletion worker.

"""
from pyqode.core import backend

if __name__ == '__main__':
    backend.CodeCompletionWorker.providers.append(
        backend.DocumentWordsProvider())
    backend.serve_forever()
