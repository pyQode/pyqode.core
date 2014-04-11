#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Simple server which adds the code_completion.DocumentWordsProvider to the
CodeCompletion worker.
"""
from pyqode.core import server_api

if __name__ == '__main__':
    server_api.CodeCompletionWorker.providers.append(
        server_api.DocumentWordsProvider())
    server_api.run()
