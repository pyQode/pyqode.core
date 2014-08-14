# -*- coding: utf-8 -*-
"""
This module contains the worker functions/classes used on the server side.

A worker is a function or a callable which receive one single argument (the
decoded json object) and returns a tuple made up of a status (bool) and a
response object (json serializable).

A worker is always tightly coupled with its caller, so are the data.

.. warning::
    This module should keep its dependencies as low as possible and fully
    supports python2 syntax. This is badly needed since the server might be run
    with a python2 interpreter. We don't want to force the user to install all
    the pyqode dependencies twice (if the user choose to run the server with
    python2, which might happen in pyqode.python to support python2 syntax).

"""
import sys
import traceback


def echo_worker(data):
    """
    Example of worker that simply echoes back the received data.

    :returns: True, data
    """
    print('echo worker running')
    return True, data


class CodeCompletionWorker(object):
    """
    This is the worker associated with the code completion mode.

    The worker does not actually do anything smart, the real work of collecting
    code completions is accomplished by the completion providers (see the
    :class:`pyqode.core.backend.workers.CodeCompletionWorker.Provider`
    interface) listed in
    :attr:`pyqode.core.backend.workers.CompletionWorker.providers`.

    Completion providers must be installed on the CodeCompletionWorker
    at the beginning of the main server script, e.g.::

        from pyqode.core.backend import CodeCompletionWorker
        CodeCompletionWorker.providers.insert(0, MyProvider())
    """
    #: The list of code completion provider to run on each completion request.
    providers = []

    class Provider(object):
        """
        This class describes the expected interface for code completion
        providers.

        You can inherit from this class but this is not required as long as you
        implement a ``complete`` method which returns the list of completions
        and have the expected signature::

            def complete(self, code, line, column, path, encoding, prefix):
                pass

        """

        def complete(self, code, line, column, path, encoding, prefix):
            """
            Returns a list of completions.

            A completion is dictionary with the following keys:

                - 'name': name of the completion, this the text displayed and
                  inserted when the user select a completion in the list
                - 'icon': an optional icon file name
                - 'tooltip': an optional tooltip string

            :param code: code string
            :param line: line number (1 based)
            :param column: column number (0 based)
            :param path: file path
            :param encoding: file encoding
            :param prefix: completion prefix (text before cursor)

            :returns: A list of completion dicts as described above.
            :rtype: list
            """
            raise NotImplementedError()

    def __call__(self, data):
        """
        Do the work (this will be called in the child process by the
        SubprocessServer).
        """
        code = data['code']
        line = data['line']
        column = data['column']
        path = data['path']
        encoding = data['encoding']
        prefix = data['prefix']
        completions = []
        for prov in CodeCompletionWorker.providers:
            try:
                results = prov.complete(
                    code, line, column, path, encoding, prefix)
                completions.append(results)
                if len(completions):
                    break
            except:
                sys.stderr.write('Failed to get completions from provider %r'
                                 % prov)
                exc1, exc2, exc3 = sys.exc_info()
                traceback.print_exception(exc1, exc2, exc3, file=sys.stderr)
        return True, completions


class DocumentWordsProvider(object):
    """
    Provides completions based on the document words
    """
    words = {}

    # word separators
    separators = [
        '~', '!', '@', '#', '$', '%', '^', '&', '*', '(', ')', '+', '{',
        '}', '|', ':', '"', "'", "<", ">", "?", ",", ".", "/", ";", '[',
        ']', '\\', '\n', '\t', '=', '-', ' '
    ]

    @staticmethod
    def split(txt, seps):
        """
        Splits a text in a meaningful list of words based on a list of word
        separators (define in pyqode.core.settings)

        :param txt: Text to split
        :param seps: List of words separators
        :return: A **set** of words found in the document (excluding
            punctuations, numbers, ...)
        """
        # replace all possible separators with a default sep
        default_sep = seps[0]
        for sep in seps[1:]:
            if sep:
                txt = txt.replace(sep, default_sep)
        # now we can split using the default_sep
        raw_words = txt.split(default_sep)
        words = set()
        for word in raw_words:
            # w = w.strip()
            if word.replace('_', '').isalpha():
                words.add(word)
        return sorted(words)

    def complete(self, code, *args):
        """
        Provides completions based on the document words.
        """
        completions = []
        for word in self.split(code, self.separators):
            completions.append({'name': word})
        return completions
