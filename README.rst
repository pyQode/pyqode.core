.. image:: https://raw.githubusercontent.com/pyQode/pyqode.core/master/doc/source/_static/pyqode-banner.png


About
-----

.. image:: http://img.shields.io/pypi/v/pyqode.core.png
   :target: https://pypi.python.org/pypi/pyqode.core/
   :alt: Latest PyPI version

.. image:: http://img.shields.io/pypi/dm/pyqode.core.png
   :target: https://pypi.python.org/pypi/pyqode.core/
   :alt: Number of PyPI downloads

.. image:: https://travis-ci.org/pyQode/pyqode.core.svg?branch=master   
   :target: https://travis-ci.org/pyQode/pyqode.core                      
   :alt: Travis-CI build status                                                                                                       

.. image:: https://coveralls.io/repos/pyQode/pyqode.core/badge.png?branch=master     
   :target: https://coveralls.io/r/pyQode/pyqode.core?branch=master       
   :alt: Coverage Status


**pyqode.core** is the core framework of the `pyQode`_ project. It contains the
base classes and a set of extensions (modes/panels/managers) that you can use
to create a code editor specialised for a given language. It also provides a
basic generic code editor that you can use as a fallback when there is no
specialised editor for a given language.

- `Issue tracker`_
- `Wiki`_
- `API reference`_


License
-------

pyQode is licensed under the MIT license.


Requirements
------------

pyqode.core depends on the following libraries:

-  Python 2 (>=2.7) or Python 3 (>= 3.2)
-  PyQt5 or PyQt4 or PySide
-  pygments


Installation
------------
You need to install PyQt or PySide by yourself.

Then you can install pyqode.core using **pip**::

    $ pip install pyqode.core

Testing
-------

pyqode.core now has a test suite and measure its coverage.

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

    
.. _Issue tracker: https://github.com/pyQode/pyQode/issues
.. _Wiki: https://github.com/pyQode/pyQode/wiki
.. _API reference: http://pyqodecore.readthedocs.org/en/latest/
