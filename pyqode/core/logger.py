#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2013 Colin Duquesnoy
#
# This file is part of pyQode.
#
# pyQode is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option) any
# later version.
#
# pyQode is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License along
# with pyQode. If not, see http://www.gnu.org/licenses/.
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
