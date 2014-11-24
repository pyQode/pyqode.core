# import sys
# from pyqode.core.backend import server
# from pyqode.core.widgets import GenericCodeEdit, TextCodeEdit
#
#
# def test_generic():
#     editor = GenericCodeEdit(
#         parent=None,
#         server_script=server.__file__, interpreter=sys.executable,
#         args=[], color_scheme='darcula', create_default_actions=True)
#     editor.file.open(__file__)
#     editor.show()
#     editor.close()
#     del editor
#
#
# def test_text():
#     editor = TextCodeEdit(
#         parent=None,
#         server_script=server.__file__, interpreter=sys.executable,
#         args=[], color_scheme='darcula', create_default_actions=True)
#     editor.file.open(__file__)
#     editor.show()
#     editor.close()
#     del editor
#
