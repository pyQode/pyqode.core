Download & Install
==================

Here you'll find all the necessary explanations for installing pyqode.core.


Requirements:
-------------

You will need to install the following packages yourself:

    - python2 >= 2.7 or python3 >= 3.2
    - setuptools
    - pip
    - PySide or PyQt4 or PyQt5

The following packages will be installed automatically:

    - pygments

.. note:: Optionally, you can install *chardet* to help pyQode detect
          file encoding automatically.

Supported platforms
-------------------

pyQode is known to run on the following platforms. It has been tested
extensively on Ubuntu 12.04 (see our `continuous integration server`_)

    - Windows: Xp, Vista, Windows 7 and Windows 8.1
    - GNU/Linux: Ubuntu , Linux Mint, Fedora and ArchLinux
    - Mac OSX (>= 10.9)

.. _continuous integration server: https://travis-ci.org/pyQode/pyqode.core

Using pip
---------

pyQode can be installed from *pypi* using `pip`_:

.. code-block:: bash

    $ pip install pyqode.core

.. _pip: https://pypi.python.org/pypi/pip

From source
-----------

You can download the `source archive`_ from the `github repository`_

Then you can install the package by opening a terminal and typing the following
commands:

.. code-block:: bash

    $ cd path/to/source/
    $ pip install .


Alternatively, you can install directly from master branch using
``pip git+https``:

.. code-block:: bash

    $ pip install git+https://github.com/pyQode/pyqode.core.git@master

.. note:: replace ``@master`` by ``@develop`` or any other valid branch name
    to install the unstable development version

.. _source archive: https://github.com/pyQode/pyqode.core/archive/master.zip
.. _github repository: https://github.com/pyQode/pyqode.core


Testing
-------

pyqode.core now has a test suite and measure its coverage.

To run the tests, you must first install tox and pytest::

    $ pip install tox pytest

You might also want to install pytest-cov and pytest-pep8.

Then you can run the tests by running the following command::

    tox

To run the tests for a specifc environment, use the -e option. E.g. to run
tests with python 2.7 and pyqt4, you would run::

    tox -e py27-pyqt4



Here is the list of test environments:

- py27-pyqt4
- py27-pyqt5
- py32-pyqt4
- py32-pyqt5
- py33-pyqt4
- py33-pyqt5
- py34-pyqt4
- py34-pyqt5
- cov
- pep8