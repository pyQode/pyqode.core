Download & Install
=========================

Here you'll find all the necessary explanations for installing pyqode.core.


Requirements:
----------------
You will need to install the following packages yourself:
    - setuptools
    - pip
    - PySide or PyQt4

The following packages will be installed automatically:
    - pygments


.. note:: Optionally, you can install chardet or chardet2 to help pyQode detect
          file encoding automatically.

.. note:: pyQode runs fine on all Windows version (from Windows XP to Windows 8)
          and has been tested on the major GNU/Linux desktop environments
          such as Unity, Gnome, Cinnamon and KDE.

          It should run fine on Mac OS too but this has never been tested.
          (Feedbacks are appreciated).

Easy install (the recommended way)
--------------------------------------

pyQode can be installed from *pypi* using *easy_install* or *pip*:

.. code-block:: bash

    $ pip install pyqode.core

From source
----------------

You can download the `source archive`_ from the `github repository`_

Then you can install the package by opening a terminal an typing the following commands:

.. code-block:: bash

    $ cd path/to/source/
    $ python setup.py install

Alternatively you can clone the repository using git:

.. code-block:: bash

    $ git clone git@github.com:ColinDuquesnoy/pyqode.core.git
    $ cd pyqode.core
    $ python setup.py install

.. _source archive: https://github.com/ColinDuquesnoy/pyqode.core/archive/master.zip
.. _github repository: https://github.com/ColinDuquesnoy/pyqode.core
