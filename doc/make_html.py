#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Call this module to creates the pyQode documentation. (Requires Sphinx to be
installed)
"""
import os
# import shutil
# try:
#     shutil.rmtree('build')
# except OSError:
#     pass
os.system("make html")
