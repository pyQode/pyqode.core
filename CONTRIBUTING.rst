Report bugs or ask a question
-----------------------------

You can report bugs or ask question on our `centralised issue tracker`_.

Submitting pull requests:
-------------------------

Pull Requests are great (on the develop branch)!

Readme/Documentation changes are ok in the master branch.

   1) Fork the Repo on github.
   2) If you are adding functionality or fixing a bug, please add a test!
   3) Add your name to AUTHORS.rst
   4) Push to your fork and submit a pull request to **the develop branch**.

The master branch is the stable branch and reflects the latest pypi version,
following the `git workflow`_

Please use **PEP8** to style your code (PEP8 compliance is tested Travis CI).

*You can check pep8 compliance before pushing by running the test suite with
the --pep8 option*::

    ($ pip install tox pytest-pep8)
    $ tox -e pep8

.. _centralised issue tracker: https://github.com/pyQode/pyQode/issues
.. _git workflow: http://nvie.com/posts/a-successful-git-branching-model/
