#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#The MIT License (MIT)
#
#Copyright (c) <2013> <Colin Duquesnoy and others, see AUTHORS.txt>
#
#Permission is hereby granted, free of charge, to any person obtaining a copy
#of this software and associated documentation files (the "Software"), to deal
#in the Software without restriction, including without limitation the rights
#to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#copies of the Software, and to permit persons to whom the Software is
#furnished to do so, subject to the following conditions:
#
#The above copyright notice and this permission notice shall be included in
#all copies or substantial portions of the Software.
#
#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
#THE SOFTWARE.
#
"""
Contains logging functions
"""
import logging


def debug(msg):
    """
    Logs a debug message. Only executed if __debug__ is set

    :param msg: Message tp log
    """
    if __debug__:
        logging.getLogger("pyqode").debug(msg)


def info(msg):
    """
    Logs an information message.

    :param msg: Message tp log
    """
    logging.getLogger("pyqode").info(msg)


def warning(msg):
    """
    Logs a warning message

    :param msg: Message tp log
    """
    logging.getLogger("pyqode").warning(msg)


def error(msg):
    """
    Logs an error message

    :param msg: Message tp log
    """
    logging.getLogger("pyqode").error(msg)


def critical(msg):
    """
    Logs a critical error message

    :param msg: Message tp log
    """
    logging.getLogger("pyqode").critical(msg)


def exception(msg):
    """
    Logs an exception
    """
    logging.getLogger("pyqode").exception(msg)


def add_handler(handler):
    """
    Adds an handler to the pyqode logger
    """
    logging.getLogger("pyqode").addHandler(handler)


def set_level(level):
    logging.getLogger("pyqode").setLevel(level)
