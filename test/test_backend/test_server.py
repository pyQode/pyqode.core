# import logging
# import os
# import sys
# from threading import Timer
# from subprocess import Popen
# from pyqode.core.backend import server
#
#
# process = None
#
#
# def test_default_parser():
#     assert server.default_parser() is not None
#
#
# def run_client_process():
#     global process
#     wd = os.path.join(os.getcwd(), 'test', 'test_backend')
#     script = os.path.join(wd, 'cli.py')
#     logging.debug('running client process')
#     process = Popen([sys.executable, script, '6789'], cwd=wd)
#
#
# def test_json_server():
#     import select
#     sys.argv[:] = []
#     sys.argv.append('server.py')
#     sys.argv.append('6789')
#     srv = server.JsonServer()
#     Timer(10, srv.server_close).start()
#     run_client_process()
#     try:
#         logging.debug('running server loop')
#         srv.serve_forever()
#     except (ValueError, select.error, IOError):
#         pass
