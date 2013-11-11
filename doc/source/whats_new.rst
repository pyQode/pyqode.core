What's New?
===========
This page lists the most prominent milestones achieved by the pyQode
developers. For more specific details about what is planned and what has been 
accomplished, please visit the `issues page on github`_ and the
:doc:`changelog </changelog>`, respectively.

Next Version
------------

Version **1.2** will focus on adding PyQt5 support and improve the API stability.

Milestones
-------------

1.1:
++++++++++

    - Add AutoComplete mode
    - Add WordClickMode
    - Add Auto save on focus out setting
    - QT_API is now case insensitive
    - Improve inter-process communication speed and reliability

1.0:
+++++++++


    - The API has been completely rewritten and renamed into pyQode.
    - It is now a namespace package; functionality are split over separate packages, pyqode.core being the foundation package.
    - It now supports both python 2.7 and python 3.3 and can works with PyQt4 or PySide.
    - The look and feel and the performances have been improved, the API is cleaner.
    - Qt designer plugins are also available.

0.2:
+++++++++
    - Add python support:

        * code completion and calltips using `Jedi`_
        * inspection and code checking using pyflakes.py and pep8.py

0.1:
+++++++++

    Initial development of PCEF with a focus on a generic code editor.


.. _`jedi`: https://github.com/davidhalter/jedi
.. _`issues page on github`: https://github.com/ColinDuquesnoy/PCEF/issues