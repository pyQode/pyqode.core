# -*- coding: utf-8 -*-
"""
Helper module for logging message. It configures a 'pyqode.core' logger that
will be used for logging events in pyqode.core.

Other namespace packages, such as pyqode.python, should have their own logger
handler so that user can make the distinction between packages.

Messages captured from the server subprocess are logged with a different
logger: pyqode.server

You will have to setup the logging module to see pyqode's log message (pyqode
does not configure anything, it's up to the application developer to setup
logging (handles, level,...)).

"""
import logging

_logger_name = 'pyqode.core'


def debug(msg):
    """
    Logs a debug message. Only executed if __debug__ is set

    :param msg: Message tp log
    """
    if __debug__:
        logging.getLogger(_logger_name).debug(msg)


def info(msg):
    """
    Logs an information message.

    :param msg: Message tp log
    """
    logging.getLogger(_logger_name).info(msg)


def warning(msg):
    """
    Logs a warning message

    :param msg: Message tp log
    """
    logging.getLogger(_logger_name).warning(msg)


def error(msg):
    """
    Logs an error message

    :param msg: Message tp log
    """
    logging.getLogger(_logger_name).error(msg)


def critical(msg):
    """
    Logs a critical error message

    :param msg: Message tp log
    """
    logging.getLogger(_logger_name).critical(msg)


def exception(msg):
    """
    Logs an exception
    """
    logging.getLogger(_logger_name).exception(msg)


def add_handler(handler):
    """
    Adds an handler to the pyqode logger
    """
    logging.getLogger(_logger_name).addHandler(handler)


def set_level(level):
    logging.getLogger(_logger_name).setLevel(level)
