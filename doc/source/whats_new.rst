What's New?
===========
This page presents the latest news concerning pyQode.

You will find information about the latest release (new feature and bugfixes) and
what is planned for the next version.

For more specific details about what is planned and what has been
accomplished, please visit the `issues page on github`_ and the
:doc:`changelog </changelog>`, respectively.

2.2.0
-----

This is mainly a bug fix version but it introduces a possible backward
incompatible change. We changed a confusing internal convention where line
numbers are 1 based and column number 0 based. Now both line and column numbers
are 0 based. This change has been done in order to make integrating pyqode
in other application an easier task. This follow the Qt Text API convention.
The only API concerned by this changed is the TextHelper API. If you were not
using TextHelper, this change won't impact your code. Otherwise you will have
to update all the line numbers arguments to be 0 based.

The only real new feature is caching of cursor position. We you re-open a document,
pyqode will try to move the cursor to the last stored position.

On top of that, we spend sometime polishing the widget and we added a few new
signals and methods to the API.

Next Version
------------

Next version will focus on adding new features!


.. _issues page on github: https://github.com/pyQode/pyqode.core/issues