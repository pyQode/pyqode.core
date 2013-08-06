#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# PCEF - Python/Qt Code Editing Framework
# Copyright 2013, Colin Duquesnoy <colin.duquesnoy@gmail.com>
#
# This software is released under the LGPLv3 license.
# You should have received a copy of the GNU Lesser General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
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
        logging.getLogger("pcef").debug(msg)


def info(msg):
    """
    Logs an information message.

    :param msg: Message tp log
    """
    logging.getLogger("pcef").info(msg)


def warning(msg):
    """
    Logs a warning message

    :param msg: Message tp log
    """
    logging.getLogger("pcef").warning(msg)


def error(msg):
    """
    Logs an error message

    :param msg: Message tp log
    """
    logging.getLogger("pcef").error(msg)


def critical(msg):
    """
    Logs a critical error message

    :param msg: Message tp log
    """
    logging.getLogger("pcef").critical(msg)
