Report bugs or ask a question
-----------------------------

You can report bugs or ask question on our bug tracker: https://github.com/pyQode/pyqode.core/issues?state=open

**Please, if your issue has been fixed in develop branch only, do not close it**. 

We leave our issues open while they have not been merged into the master branch (i.e. while the fix has not officially been released).

*Note: we are now using [waffle.io](https://waffle.io/pyqode/pyqode.core) to manage all pyqode issues (from all
sub repositories).


Submitting pull requests:
-------------------------

Pull Requests are great (on the dev branch)!

Readme/Documentation changes are ok in the master branch.

   1) Fork the Repo on github.
   2) Add your name to AUTHORS.txt
   3) Push to your fork and submit a pull request to the dev branch.

The master branch is used for the stable releases, following the
[git workflow](http://nvie.com/posts/a-successful-git-branching-model/)

Please use **PEP8** to style your code (PEP8 compliance is tested Travis CI). You
can check pep8 compliance before pushing by running the test suite with the --pep8 option::

    ($ pip3 install pytest-pep8)
    $ python3 runtests.py --pep8
