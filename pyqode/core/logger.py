# -*- coding: utf-8 -*-
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
