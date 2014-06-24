#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Call this module to creates the pyQode documentation. (Requires Sphinx to be
installed)
"""
import os
import shutil
shutil.rmtree('build')
os.system("make html")
