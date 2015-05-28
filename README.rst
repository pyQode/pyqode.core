.. image:: https://raw.githubusercontent.com/pyQode/pyQode/master/media/pyqode-banner.png

|

.. image:: https://img.shields.io/pypi/v/pyqode.core.svg
   :target: https://pypi.python.org/pypi/pyqode.core/
   :alt: Latest PyPI version

.. image:: https://img.shields.io/pypi/dm/pyqode.core.svg
   :target: https://pypi.python.org/pypi/pyqode.core/
   :alt: Number of PyPI downloads

.. image:: https://img.shields.io/pypi/l/pyqode.core.svg

.. image:: https://travis-ci.org/pyQode/pyqode.core.svg?branch=master
   :target: https://travis-ci.org/pyQode/pyqode.core
   :alt: Travis-CI build status


.. image:: https://coveralls.io/repos/pyQode/pyqode.core/badge.svg?branch=master
   :target: https://coveralls.io/r/pyQode/pyqode.core?branch=master
   :alt: Coverage Status

About
-----
**pyqode.core** is the core framework of the `pyQode`_ project.

It contains the base classes and a set of extensions (modes/panels/managers)
needed to develop a specialised code editor.

It also provides a basic generic code editor that you can use as a fallback
when there is no specialised editor for a given language.

- `Issue tracker`_
- `Wiki`_
- `API reference`_
- `Contributing`_
- `Changelog`_
- `Screenshots`_


Requirements
------------

pyqode.core depends on the following libraries:

- Python 2 (**>=2.7**) or Python 3 (**>= 3.2**)
- PyQt5 or PyQt4 or PySide
- pygments
- pyqode.qt
- future
- qtawesome (optional)


Installation
------------
You need to install PyQt or PySide by yourself. Note that you should prefer
**PyQt5 on Mac OSX** (retina screen support, better integration).

Then you can install pyqode.core using **pip**::

    $ pip install pyqode.core --upgrade

Testing
-------

pyqode.core has a test suite and measure its coverage.

To run the tests, you must first install tox and pytest::

    $ pip install tox pytest

You might also want to install pytest-cov and pytest-pep8.

Then you can run the tests by running the following command::

    $ tox

To run the tests for a specifc environment, use the -e option. E.g. to run
tests with python 2.7 and pyqt4, you would run::

    $ tox -e py27-pyqt4

Here is the list of available test environments:

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


.. _Changelog: https://github.com/pyQode/pyqode.core/blob/master/CHANGELOG.rst
.. _Contributing: https://github.com/pyQode/pyqode.core/blob/master/CONTRIBUTING.rst
.. _pyQode: https://github.com/pyQode/pyQode
.. _Screenshots: https://github.com/pyQode/pyQode/wiki/Screenshots-and-videos#pyqodecore-screenshots
.. _Issue tracker: https://github.com/pyQode/pyQode/issues
.. _Wiki: https://github.com/pyQode/pyQode/wiki
.. _API reference: https://pythonhosted.org/pyqode.core/
