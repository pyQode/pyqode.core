#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Simple server which adds the code_completion.DocumentWordsProvider to the
CodeCompletion worker.
"""
from pyqode.core.api import code_completion
from pyqode.core.api import server
from pyqode.core.api import workers

if __name__ == '__main__':
    workers.CodeCompletion.providers.append(
        code_completion.DocumentWordsProvider())
    server.run()
