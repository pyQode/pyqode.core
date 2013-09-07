.. Copyright 2013 Colin Duquesnoy
.. This file is part of pyQode.

.. pyQode is free software: you can redistribute it and/or modify it under
.. the terms of the GNU Lesser General Public License as published by the Free
.. Software Foundation, either version 3 of the License, or (at your option) any
.. later version.
.. pyQode is distributed in the hope that it will be useful, but WITHOUT
.. ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
.. FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
.. details.

.. You should have received a copy of the GNU Lesser General Public License along
.. with pyQode. If not, see http://www.gnu.org/licenses/.

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

Easy install
---------------

pyQode can be installed from pypi using easy_install or pip:

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
