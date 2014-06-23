"""
The backend package contains the API to use on the server side:
    - server + methods for running it
    - workers definitions
"""
# server
from .server import JsonServer
from .server import default_parser
from .server import serve_forever

# workers
from .workers import CodeCompletionWorker
from .workers import DocumentWordsProvider
from .workers import echo_worker


class NotConnected(Exception):
    """
    Raised if the client is not connected to the server when an operation
    is requested.
    """
    def __init__(self):
        super().__init__('Client socket not connected or '
                         'server not started')


__all__ = [
    'JsonServer',
    'default_parser',
    'serve_forever',
    'CodeCompletionWorker',
    'DocumentWordsProvider',
    'echo_worker',
    'NotConnected'
]
