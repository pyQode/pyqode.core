# -*- coding: utf-8 -*-
import os
import pytest
from pyqode.core import panels
from pyqode.qt.QtTest import QTest
from test.helpers import preserve_editor_config


PATH = pth = os.path.join(os.getcwd(), 'test', 'files', 'big5hkscs.txt')


def test_open(editor):
    editor.file.open(__file__, encoding='utf-8')
    assert editor.file.path == __file__
    assert editor.file.extension == '.py'
    assert editor.file.dirname == os.path.join(os.getcwd(), 'test',
                                               'test_managers')
    assert editor.file.icon is not None
    assert editor.file.mimetype == 'text/x-python'


def test_open_non_existing_file(editor):
    with pytest.raises(IOError):
        editor.file.open('qzdjoi')


@preserve_editor_config
def test_encodings(editor):
    with pytest.raises(UnicodeDecodeError):
        editor.file.open(PATH, encoding='utf-8', use_cached_encoding=False)
    editor.panels.append(panels.EncodingPanel(),
                         panels.EncodingPanel.Position.TOP)
    editor.file.open(pth, encoding='utf-8', use_cached_encoding=False)
    QTest.qWait(1000)
    assert editor.panels.get(panels.EncodingPanel).isVisible() is True


def test_reload(editor):
    editor.file.open(PATH, encoding='big5hkscs', use_cached_encoding=False)
    editor.file.reload('cp1250')


def test_close(editor):
    editor.file.open(__file__)
    editor.file.close()
    assert editor.file.path == ''
    assert editor.file.mimetype == ''
