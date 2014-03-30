# -*- coding: utf-8 -*-
"""
The public API consists of a series of modules that addresses a specific
concern of pyqode:
  - text: text manipulation functions (selection, insertion, cursor
          manipulation, queries).
  - server: api for writing/configuring the pyqode server.
  - classes: the base classes needed to extend the code editor widget (mode,
             panels, text decoration, textblock user data,...)
  - utils: utitlies that might be useful when extending pyqode (
    job runner, memoize,...)

.. todo: At the moment the api is mostly empty, I have to move existing
         pyqode.core classes here and refactor a lot of the internal to make
         the new text api module.
"""
