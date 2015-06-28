# -*- coding: utf-8 -*-
import os
import pytest
from pyqode.core import panels
from pyqode.core.managers import FileManager
from pyqode.qt.QtTest import QTest


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
    with pytest.raises(OSError):
        editor.file.open('qzdjoi')


def test_encodings(editor):
    with pytest.raises(UnicodeDecodeError):
        editor.file.open(PATH, encoding='utf-8', use_cached_encoding=False)
    editor.panels.append(panels.EncodingPanel(),
                         panels.EncodingPanel.Position.TOP)
    editor.file.open(pth, encoding='utf-8', use_cached_encoding=False)
    editor.show()
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


@pytest.mark.parametrize('system, eol', [
    ('mac', '\r'), ('linux', '\n'), ('windows', '\r\n')
])
def test_auto_detect_eol(editor, system, eol):
    filename = '%s_eol.txt' % system
    with open(filename, 'wb') as f:
        f.write(b'First line' + eol.encode('utf-8') + b'Second line')
    editor.file.autodetect_eol = True
    editor.file.open(filename)
    assert editor.file._eol == eol
    editor.file.save()
    with open(filename, 'Ur') as f:
        print(f.read())
        assert f.newlines == eol
    os.remove(filename)


@pytest.mark.parametrize('preferred_eol', [
    FileManager.EOL.Mac,
    FileManager.EOL.Linux,
    FileManager.EOL.Windows,
    FileManager.EOL.System
])
def test_preferred_encodings(editor, preferred_eol):
    fn = 'test_eol.txt'
    with open(fn, 'w') as f:
        f.write('First line\nSecond line')
    editor.file.autodetect_eol = False
    editor.file.preferred_eol = preferred_eol
    editor.file.open(fn)
    assert editor.file._eol == editor.file.EOL.string(preferred_eol)
    editor.appendPlainText('some text')
    editor.file.save()
    with open(fn, 'Ur') as f:
        print(f.read())
        assert f.newlines == editor.file.EOL.string(preferred_eol)
    os.remove(fn)
