"""
This example show you how to setup a code completion provider on the backend

(the provider will be automatically used when the user request a code
completion).
"""
from pyqode.core import backend


class CustomCodeCompletionProvider:
    def complete(self, code, *args):
        """
        Provides a static code completion list

        :param code: code to complete
        :param args: additional (unused) arguments.
        """
        return [
            {'name': 'Code'},
            {'name': 'completion'},
            {'name': 'example'}
        ]

if __name__ == '__main__':
    backend.CodeCompletionWorker.providers.append(
        CustomCodeCompletionProvider())
    backend.serve_forever()
