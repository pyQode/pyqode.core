# -*- coding: utf-8 -*-
"""
Contains utility functions
"""
import functools
import logging
from pyqode.qt import QtCore, QtWidgets, QtGui


def _logger():
    """ Returns module logger """
    return logging.getLogger(__name__)


class memoized(object):  # pylint: disable=invalid-name, too-few-public-methods
    """
    Decorator. Caches a function's return value each time it is called.
    If called later with the same arguments, the cached value is returned
    (not reevaluated).
    """
    def __init__(self, func):
        self.func = func
        self.cache = {}

    def __call__(self, *args):
        try:
            if args in self.cache:
                return self.cache[args]
            else:
                value = self.func(*args)
                self.cache[args] = value
                return value
        except TypeError:
            return self.func(*args)

    def __repr__(self):
        """ Return the function's docstring."""
        return self.func.__doc__

    def __get__(self, obj, objtype):
        """ Support instance methods. """
        return functools.partial(self.__call__, obj)


def drift_color(base_color, factor=110):
    """
    Return color that is lighter or darker than the base color.

    If base_color.lightness is higher than 128, the returned color is darker
    otherwise is is lighter.

    :param base_color: The base color to drift from
    :return A lighter or darker color.
    """
    base_color = QtGui.QColor(base_color)
    if base_color.lightness() > 128:
        return base_color.darker(factor)
    else:
        if base_color == QtGui.QColor('#000000'):
            return QtGui.QColor('#202020')
        else:
            return base_color.lighter(factor + 10)


class TextStyle(object):  # pylint: disable=too-few-public-methods
    """
    Helper class to define a text format. This class has methods to set the
    text style from a string and to easily be created from a string, making
    serialisation extremely easy.

    A text style is made up of a text color and a series of text attributes:

        - bold/nbold
        - italic/nitalic
        - underlined/nunderlined.

    Example of usage::

        style = TextStyle('#808000 nbold nitalic nunderlined')
        print(style)  #should print '#808000 nbold nitalic nunderlined'

    """

    def __init__(self, style=None):
        """
        :param style: The style string ("#rrggbb [bold] [italic] [underlined])
        """
        self.color = QtGui.QColor()
        self.bold = False
        self.italic = False
        self.underlined = False
        if style:
            self.from_string(style)

    def __repr__(self):
        color = self.color.name()
        bold = "nbold"
        if self.bold:
            bold = "bold"
        italic = "nitalic"
        if self.italic:
            italic = "italic"
        underlined = "nunderlined"
        if self.underlined:
            underlined = "underlined"
        return " ".join([color, bold, italic, underlined])

    @memoized
    def from_string(self, string):
        """ Makes TextStyles from a string """
        tokens = string.split(" ")
        assert len(tokens) == 4
        self.color = QtGui.QColor(tokens[0])
        self.bold = False
        if tokens[1] == "bold":
            self.bold = True
        self.italic = False
        if tokens[2] == "italic":
            self.italic = True
        self.underlined = False
        if tokens[3] == "underlined":
            self.underlined = True


class DelayJobRunner(object):
    """
    Utility class for running job after a certain delay. If a new request is
    made during this delay, the previous request is dropped and the timer is
    restarted for the new request.

    We use this to implement a cooldown effect that prevents jobs from being
    executed while the IDE is not idle.

    A job is a simple callable.
    """
    def __init__(self, delay=500):
        """
        :param delay: Delay to wait before running the job. This delay applies
        to all requests and cannot be changed afterwards.
        """
        self._timer = QtCore.QTimer()
        self._interval = delay
        self._timer.timeout.connect(self._exec_requested_job)
        self._args = []
        self._kwargs = {}
        self._job = lambda x: None

    def __del__(self):
        self.cancel_requests()

    def request_job(self, job, *args, **kwargs):
        """
        Request a job execution. The job will be executed after the delay
        specified in the DelayJobRunner contructor elapsed if no other job is
        requested until then.

        :param job: job.
        :type job: callable

        :param force: Specify if we must force the job execution by stopping
                      the job that is currently running (if any).
        :type force: bool

        :param args: args
        :param kwargs: kwargs
        """
        self.cancel_requests()
        self._job = job
        self._args = args
        self._kwargs = kwargs
        self._timer.start(self._interval)

    def cancel_requests(self):
        """
        Cancels pending requests.
        """
        self._timer.stop()

    def _exec_requested_job(self):
        """
        Execute the requested job after the timer has timeout.
        """
        self._timer.stop()
        self._job(*self._args, **self._kwargs)


def show_wait_cursor(func):
    """
    Decorator that show a wait cursor the time to execute the wrapped function.
    The cursor is automatically restored once the method returned.
    """
    @functools.wraps(func)
    def wrapper(editor, *args, **kwds):
        """ Decorator """
        editor.set_mouse_cursor(QtCore.Qt.WaitCursor)
        ret_val = func(editor, *args, **kwds)
        editor.set_mouse_cursor(QtCore.Qt.IBeamCursor)
        return ret_val
    return wrapper


class Action:
    """
    Utility class used to describe a QAction:
        - text: text of the action (used as QAction text)
        - shortcut: QtGui.QKeySequence or string used to setup the action
          shortcut.
        - icon: optional icon associated with the action.

    """
    def __init__(self, text, shortcut='', icon=('', '')):
        """
        :param text: text of the action
        :param shortcut: QtGui.QKeySequence string associated with the action.
            Optional.
        :param icon: icon associated with the action. This can be a string or
            a tuple of strings to create an action from theme (theme, fallback)
        """
        self.text = text
        self.shortcut = shortcut
        self.icon = icon

    def make_icon(self):
        """ Make an icon from the action icon definition """
        if isinstance(self.icon, tuple):
            theme, icon = self.icon
            return QtGui.QIcon.fromTheme(theme, QtGui.QIcon(icon))
        else:
            QtGui.QIcon(self.icon)

    def make_action(self, parent):
        """ Make a QAction out of the action properties """
        a = QtWidgets.QAction(parent)
        a.setText(self.text)
        a.setShortcut(self.shortcut)
        if self.icon:
            a.setIcon(self.make_icon())
        return a

    def __repr__(self):
        return ('Action(%r, shortcut=%r icon=%r)' %
                (self.text, self.shortcut, self.icon))
