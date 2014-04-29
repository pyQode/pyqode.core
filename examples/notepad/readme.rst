This directory contains a complete application based on pyqode.core.

It uses *most of the pyqode.core features* and comes with packaging scripts to
show you how to distribute a pyqode based application.

To **run** the example, just run::

    python3 notepad.py


To **install** the package *on linux*, just run::

    sudo python3 setup.py install

To **freeze the application on Windows**, you first need to install cx_Freeze.
Then you can run::

    python freeze_setup.py build

The resulting binary can be found in the **bin/** folder.

Additionally you can install InnoSetup and run setup.iss to build an installer
out of the frozen app (the resulting installer can be found in the **dist**
folder).
