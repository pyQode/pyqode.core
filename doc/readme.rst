This directory contains the source for building the API reference
documentation.

To build the documentation, just run::

    make html

To update the API reference (e.g. to include new module):

    - delete the rst file for the concerned module to force apidoc to update
      the module.

cd .. && sphinx-apidoc -e -F -o apidoc pyqode && cd doc
