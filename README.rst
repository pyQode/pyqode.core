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

To run the tests, just run ``python setup.py test``

To measure coverage, run::

    python setup.py test -a "--cov pyqode"

To check for PEP8 warnings, install pytest-pep8 and run::

    python setup.py test -a "--pep8 -m pep8"


To run a single test, use ``-a "-- test_file_path.py::test_function"``, e.g.::

    python setup.py test -a "-- test/test_api/test_code_edit.py::test_set_plain_text"


Testing Matrix
++++++++++++++

We test the following combinations on Travis-CI:

+--------------------------+---------+---------+
|                          | PyQt4   | PyQt5   |
+==========================+=========+=========+
| GNU/Linux - Python 2.7   | yes     | no      |
+--------------------------+---------+---------+
| GNU/Linux - Python 3.4   | yes     | yes     |
+--------------------------+---------+---------+



.. _Changelog: https://github.com/pyQode/pyqode.core/blob/master/CHANGELOG.rst
.. _Contributing: https://github.com/pyQode/pyqode.core/blob/master/CONTRIBUTING.rst
.. _pyQode: https://github.com/pyQode/pyQode
.. _Screenshots: https://github.com/pyQode/pyQode/wiki/Screenshots-and-videos#pyqodecore-screenshots
.. _Issue tracker: https://github.com/pyQode/pyQode/issues
.. _Wiki: https://github.com/pyQode/pyQode/wiki
.. _API reference: https://pythonhosted.org/pyqode.core/
