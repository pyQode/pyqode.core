"""
A helper module for testing, introducing some helper functions. Inspired by
the jedi helper module for their testing package
"""
import os
from os.path import abspath, dirname
import functools

test_dir = dirname(abspath(__file__))


def cwd_at(path):
    """
    Decorator to run function at `path`.

    :type path: str
    :arg path: relative path from repository root (e.g., ``'jedi'``).
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