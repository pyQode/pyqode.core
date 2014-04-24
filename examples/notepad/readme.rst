This directory contains a complete application based on pyqode.

It uses most of the pyqode.core features and comes with packaging scripts to
show you how to setup a pyqode application and how to distribute it (
especially on Windows with cx_Freeze)

The notepad package is made up of three files:

    - __init__.py: contains the main function of the application
    - main_window: contains the implementation of the main window
    - editor: contains our custom CodeEdit definition

To run the example, just run::

    python3 notepad.py


To install the package on linux, just run::

    sudo python3 setup.py install

To freeze the application on Windows, you first need to install cx_Freeze. Then
you can run::

    python freeze_setup.py build
