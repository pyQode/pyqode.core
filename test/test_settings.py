"""
Test pyqode.core.settings
"""
import locale
import pytest
from pyqode.core.api import convert_to_codec_key
from pyqode.core.settings import Settings


def test_preferred_encodings():
    s = Settings(suffix='-pytest')
    s.clear()
    encodings = s.preferred_encodings
    assert len(encodings) == 1
    assert encodings[0] == convert_to_codec_key(
        locale.getpreferredencoding())
    encodings.append('utf_16')
    s.preferred_encodings = encodings
    s = Settings(suffix='-pytest')
    assert 'utf_16' in s.preferred_encodings


def test_cached_encodings():
    s = Settings(suffix='-pytest')
    s.clear()
    # not in cache
    with pytest.raises(KeyError):
        s.get_file_encoding(__file__)
    s.set_file_encoding(__file__, 'utf_16')
    s = Settings(suffix='-pytest')
    assert s.get_file_encoding(__file__) == 'utf_16'
