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

Welcome to pyQode documentation!
=======================================

pyQode is a flexible source code editor widget library for Python/Qt applications.

pyQode is a **namespace package** made up of the following official packages:

    * `pyqode.core`_: The foundation package. Defines the base classes and provides a set of generic modes and panels that can be used for any kind of code editor widget.

    * `pyqode.python`_: Add python support to pyqode (code completion, calltips, live code checking,...)

    * `pyqode.widgets`_: A set of useful widgets that can be used to speed up the development of pyqode applications (property grid, tab widget,...)

    * `pyqode.designer`_: Startup script that starts Qt Designer with the installed pyqode plugins

This documentation will only cover the `pyqode.core`_ package.


.. image:: _static/screenshot.png
    :alt: QGenericCodeEdit on Linux Mint 15 Cinnamon
    :width: 400
    :height: 300
    :align: center

Parts of the documentation:
============================

.. toctree::
    :maxdepth: 1
    :hidden:

    whats_new
    download
    getting_started
    advanced
    examples
    changelog
    api/api_doc
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

      :doc:`api`
         The api reference documentation


Meta information:
============================

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
============================

* :ref:`genindex`

* :ref:`search`


.. _pyqode.core: https://github.com/ColinDuquesnoy/pyqode.core
.. _pyqode.python: https://github.com/ColinDuquesnoy/pyqode.python
.. _pyqode.widgets: https://github.com/ColinDuquesnoy/pyqode.widgets
.. _pyqode.designer: https://github.com/ColinDuquesnoy/pyqode.designer
