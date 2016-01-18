.. image:: https://raw.githubusercontent.com/pyQode/pyQode/master/media/pyqode-banner.png

|

.. image:: https://img.shields.io/pypi/v/pyqode.core.svg
   :target: https://pypi.python.org/pypi/pyqode.core/
   :alt: Latest PyPI version

.. image:: https://img.shields.io/pypi/dm/pyqode.core.svg
   :target: https://pypi.python.org/pypi/pyqode.core/
   :alt: Number of PyPI downloads

.. image:: https://img.shields.io/pypi/l/pyqode.core.svg

.. image:: https://semaphoreci.com/api/v1/projects/7b0daa6b-f30f-4d00-a8e3-cf4f9943f7fc/664079/shields_badge.svg
   :target: https://semaphoreci.com/colinduquesnoy/pyqode-core
   :alt: Semaphore CI build status

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

To run the tests, just run runtests.py with the interpreter you want
to run the test suite::

    python2.7 runtests.py
    python3.4 runtests.py

To measure coverage, install pytest-cov package and run::

    python runtests.py --cov pyqode

To check for PEP8 warnings, use:

    python runtests.py --pep8 -m pep8

.. _Changelog: https://github.com/pyQode/pyqode.core/blob/master/CHANGELOG.rst
.. _Contributing: https://github.com/pyQode/pyqode.core/blob/master/CONTRIBUTING.rst
.. _pyQode: https://github.com/pyQode/pyQode
.. _Screenshots: https://github.com/pyQode/pyQode/wiki/Screenshots-and-videos#pyqodecore-screenshots
.. _Issue tracker: https://github.com/pyQode/pyQode/issues
.. _Wiki: https://github.com/pyQode/pyQode/wiki
.. _API reference: https://pythonhosted.org/pyqode.core/
