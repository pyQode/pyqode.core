from pyqode.core.api import encodings


def test_convert_to_code_key():
    assert encodings.convert_to_codec_key('UTF-8') == 'utf_8'
