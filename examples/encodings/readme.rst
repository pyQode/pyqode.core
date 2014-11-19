This directory contains examples showing various way to deal with text 
encodings issues:

- error.py:
  no error management, program exit with a traceback.
- panel.py: 
  use the ``EncodingPanel`` to automatically handle decoding errors 
- dialog.py: 
  catch UnicodeDecodingError and show an encoding dialog to let the user 
  reload the file with another encoding
- menu.py:
  catch UnicodeDecodingError and show a message box to tell the user to 
  reload the file using the editor context menu
- detect.py:
  use ``chardet`` to detect the file encoding and use the ``EncodingPanel`` 
  in case of decoding error


All the above examples accept one command line argument which is the path to the
file to open. In case there is no file path argument, all example will open 
``test/files/big5hkscs.txt`` (a text file encoded in big5, a chinese encoding).
