#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Simple server which adds the code_completion.DocumentWordsProvider to the
CodeCompletion worker.
"""
from pyqode.core import server
from pyqode.core import workers

if __name__ == '__main__':
    workers.CodeCompletion.providers.append(
        workers.DocumentWordsProvider())
    server.run()
