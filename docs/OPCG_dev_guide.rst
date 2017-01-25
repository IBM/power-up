.. highlight:: none

Developer Guide
===============

Cluster Genesis is developed by a team of IBM engineers.

Git Repository Model
--------------------

Development and test is orchestrated within the  *master* branch. Stable
*release-x.y* branches are created off *master* and supported with bug fixes.
`Semantic Versioning <http://semver.org/>`_ is used for release tags and branch
names.

Commit Message Rules
--------------------

- Subject line
    - First line of commit message provides a short description of change
    - Must not exceed 50 characters
    - First word after tag must be capitalized
    - Must begin with one of the follwoing subject tags::

        feat:      New feature
        fix:       Bug fix
        docs:      Documentation change
        style:     Formatting change
        refactor:  Code change without new feature
        test:      Tests change
        chore:     Miscellaneous no code change

- Body
    - Single blank line seperates subject line and message body
    - Contains detailed description of change
    - Lines must not exceed 72 characters
    - Periods must be followed by single space

Unit Tests and Linters
----------------------

Tox
~~~

Tox is used to manage python virtual environments used to run unit tests and
various linters.

To run tox first install python dependencies::

    cluster-genesis$ ./scripts/install.py

To run all tox test environments::

    cluster-genesis$ tox

List test environments::

    cluster-genesis$ tox -l
    py27
    bashate
    pep8
    ansible-lint

Run only 'pep8' test environment::

    cluster-genesis$ tox -e pep8

Unit Test
~~~~~~~~~

Unit test scripts reside in the `cluster-genesis/tests/unit/` directory.

Unit tests can be run through tox::

    cluster-genesis$ tox -e py27

Or called directly through python (be mindful of your python environment!)::

    cluster-genesis$ python -m unittest discover

Linters
~~~~~~~

Linters are required to run cleanly before a commit is submitted. The following
linters are used:

- Bash: bashate
- Python: pep8/flake8
- Ansible: ansible-lint

Linters can be run through tox::

    cluster-genesis$ tox -e bashate
    cluster-genesis$ tox -e pep8
    cluster-genesis$ tox -e ansible-lint

Or called directly (again, be mindful of your python environment!)
