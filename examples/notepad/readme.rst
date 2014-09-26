This directory contains a complete application based on pyqode.core.

It uses *most of the pyqode.core features* and comes with packaging scripts to
show you how to distribute a pyqode based application.

To **run** the example, just run::

    python notepad.py


To **install** the package *on linux*, just run::

    sudo python setup.py install

To **freeze the application on Windows**, you first need to install cx_Freeze.
Then you can run::

    python freeze_setup.py build

The resulting binary can be found in the **bin/** folder.

Additionally you can install InnoSetup and run setup.iss to build an installer
out of the frozen app (the resulting installer can be found in the **dist**
folder).


..note:: Notepad uses pyqode.qt package, this means it can run on PyQt5 or PyQt4 or PySide
         (we use the pyqt_distutils and pyqode-uic packages to build the ui scripts for
          all qt backends).
