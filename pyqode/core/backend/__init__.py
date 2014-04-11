"""
The backend package contains the API for to use server side:
    - server + methods for running it
    - workers definitions
"""
# server
from pyqode.core.backend.server import JsonServer
from pyqode.core.backend.server import default_parser
from pyqode.core.backend.server import serve_forever

# workers
from pyqode.core.backend.workers import CodeCompletionWorker
from pyqode.core.backend.workers import DocumentWordsProvider
from pyqode.core.backend.workers import echo_worker
