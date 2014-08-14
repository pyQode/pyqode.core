What's New?
===========
This page presents the latest news concerning pyQode.

You will find information about the latest release (new feature and bugfixes) and
what is planned for the next version.

For more specific details about what is planned and what has been
accomplished, please visit the `issues page on github`_ and the
:doc:`changelog </changelog>`, respectively.

2.1.0
-----

The 2.1 version brings back the code folding panel and API (the new API is
faster and a lot more stable than the previous one, it also allows more
features such as parent scopes highlighting, docstring and imports folding
for python,...)

The other major new feature is that pyqode now provides an API for handling
encoding errors. We removed automatic charset detection and gives the user some
means to reload an editor with another encoding. The new encoding panel or the
encodings dialog can be used for that purpose.


We also improved existing modes and panels:

  - the syntax highlighter has been reviewed, it is now possible to use
    pygments styles for native highlighters. Native highlighters are also faster
    than before.
  - improved checker modes: there is no more limitation for the number of
    messages and the mode does remove only the message that have disappeared
    from the linter's results. There is a new panel dedicated to rendering
    checker panels (MarkerPanel is now a general purpose icon panel, e.g. to
    draw breakpoints or bookmarks).


We also fixed quite a lots of small minor bugs (such as wrong cursor position after
duplicate line,...).

To make your life easier (at least when you're starting with pyqode) we added
some premade editors:

   - TextCodeEdit: simple code edit specialised for plain text (pretty fast
     for long files such as log files,...)
   - GenericCodeEdit: generic code edit with basic support for a lots of
                      languages but much slower and lot less smarted than a
                      dedicated code edit.



Next Version
------------

Next version will focus on adding new features!


.. _issues page on github: https://github.com/pyQode/pyqode.core/issues