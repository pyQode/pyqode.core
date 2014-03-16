"""
A helper module for testing, introducing some helper functions. Inspired by
the jedi helper module for their testing package
"""
import os
from os.path import abspath, dirname
import functools
import platform

test_dir = dirname(abspath(__file__))


def cwd_at(path):
    """
    Decorator to run function at `path`.

    :type path: str
    :arg path: relative path from repository root (e.g., 'pyqode' or 'test').
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwds):
            try:
                oldcwd = os.getcwd()
                repo_root = os.path.dirname(test_dir)
                os.chdir(os.path.join(repo_root, path))
                return func(*args, **kwds)
            finally:
                os.chdir(oldcwd)
        return wrapper
    return decorator


def python2_path():
            return '/usr/bin/python' if platform.system() == 'Linux' else \
                'c:\\Python27\\python.exe'


def require_python2():
    """
    Decorator to skip tests that require python2 when python2 is not available

    The expected python2 path is '/usr/bin/python' on Linux and
    'c:\Python27\python.exe' on Windows.
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwds):
            if os.path.exists(python2_path()):
                return func(*args, **kwds)
        return wrapper
    return decorator