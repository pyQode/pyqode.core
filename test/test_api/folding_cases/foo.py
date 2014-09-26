"""
This file contains some tricky corner case for the code folding detector
and panel. We use it in their respective tests
"""
import os
import sys


class Foo(object):
    """
    Foo class
    """
    class_attr = None

    def bar(self, spam, egg):



        def bar2(spam, egg):
            def bar3(spam, egg):
                pass
        pass

    def spam(self):
        """
        Spam
        """
        pass

varuable = [
    1,
    2
]


def foo():
    """ Foo """
    pass