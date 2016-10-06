=============================================================
PIP Chill - Make requirements will only the packages you need
=============================================================


.. image:: https://img.shields.io/pypi/v/pip_chill.svg
        :target: https://pypi.python.org/pypi/pip_chill

.. image:: https://img.shields.io/travis/rbanffy/pip_chill.svg
        :target: https://travis-ci.org/rbanffy/pip_chill

.. image:: https://readthedocs.org/projects/pip-chill/badge/?version=latest
        :target: https://pip-chill.readthedocs.io/en/latest/?badge=latest
        :alt: Documentation Status

.. image:: https://pyup.io/repos/github/rbanffy/pip_chill/shield.svg
     :target: https://pyup.io/repos/github/rbanffy/pip_chill/
     :alt: Updates


Like `pip freeze` but lists only the packages that are not
dependencies of installed packages.


* Free software: GNU General Public License v3
* Documentation: https://pip-chill.readthedocs.io.


Features
--------

Generates a requirements file without any packages that depend on
other packages in the file.

Usage
-----

Suppose you have installed in your virtualenv a couple packages. When
you run `pip freeze`, you'll get a list of all packages installed,
with all dependencies. If one of the packages you installed ceases to
depend on an already installed package, you have to manually remove it
from the list. The list also makes no distinction about the packages
you actually care about and packages your packages care about, making
the requirements file bloated and, ultimately, inaccurate.

Credits
-------

This package was created with Cookiecutter_ and the
`audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
