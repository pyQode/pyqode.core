"""
Test pyqode.core.settings
"""
import os
import locale
import pytest
from pyqode.core.api import convert_to_codec_key
from pyqode.core.cache import Cache


def test_preferred_encodings():
    cache = Cache(suffix='-pytest')
    cache.clear()
    encodings = cache.preferred_encodings
    assert len(encodings) == 1
    assert encodings[0] == convert_to_codec_key(
        locale.getpreferredencoding())
    encodings.append('utf_16')
    cache.preferred_encodings = encodings
    cache2 = Cache(suffix='-pytest')
    assert 'utf_16' in cache2.preferred_encodings


def test_cached_encodings():
    s = Cache(suffix='-pytest')
    s.clear()
    # not in cache
    with pytest.raises(KeyError):
        s.get_file_encoding(os.path.join(os.getcwd(), 'test', 'files',
                                         'big5hkscs.txt'))
    s.set_file_encoding(__file__, 'utf_16')
    s = Cache(suffix='-pytest')
    assert s.get_file_encoding(__file__) == 'utf_16'
