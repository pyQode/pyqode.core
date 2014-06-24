Welcome to pyQode documentation!
================================

pyQode is a *flexible source code editor widget* for PyQt/PySide applications.

**pyQode is a library/widget, not an IDE**. *You can see it as an alternative
to QScintilla.*

pyQode is organised as a **namespace package** made up of the following
official packages:

  - `pyqode.core`_: core package
  - `pyqode.python`_: python support (code completion, ...)
  - `pyqode.designer`_: Starts Qt designer with all pyqode plugins

**pyqode.core** is the foundation package, it contains the base classes
(CodeEdit, Mode, Panel) and a set of builtin modes and panels that are useful
for any kind of code editor. With ``pyqode.core`` you can already create a
generic code editor (similar to gedit, leafpad, notepad++, ...) with only a
few lines of code.

This documentation will only cover the `pyqode.core`_ package.


.. image:: _static/notepad.png
    :alt: Screenshot of notepad example
    :width: 400
    :height: 300
    :align: center


Parts of the documentation:
===========================

.. toctree::
    :maxdepth: 1
    :hidden:

    whats_new
    download
    getting_started
    advanced
    examples
    api/index
    changelog
    bugs
    contribute
    license
    credits


.. hlist::
   :columns: 2

   * .. glossary::

      :doc:`whats_new`
         What's new since the last release, and what is planned for the next one.

   * .. glossary::

      :doc:`download`
         Instructions on where and how to install pyQode.

   * .. glossary::

      :doc:`getting_started`
         A gentle introduction to pyQode, covering some basic principles.

   * .. glossary::

      :doc:`advanced`
         A more in depth approach to pyQode, covering advanced features

   * .. glossary::

      :doc:`examples`
         Practical examples demonstrating how to use the framework.

   * .. glossary::

      :doc:`api/index`
         The api reference documentation


Meta information:
=================

.. hlist::
   :columns: 2

   * .. glossary::

      :doc:`bugs`
        How to report bugs

   * .. glossary::

      :doc:`contribute`
        How to contribute

   * .. glossary::

      :doc:`license`
        pyQode license

   * .. glossary::

      :doc:`credits`
        Credits to contributors and external libraries


Indices and tables:
===================

* :ref:`genindex`

* :ref:`search`


.. _pyqode.core: https://github.com/pyQode/pyqode.core
.. _pyqode.python: https://github.com/pyQode/pyqode.python
.. _pyqode.widgets: https://github.com/pyQode/pyqode.widgets
.. _pyqode.designer: https://github.com/pyQode/pyqode.designer
