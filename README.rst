=============================================================
PIP Chill - Make requirements with only the packages you need
=============================================================


.. image:: https://img.shields.io/pypi/v/pip-chill.svg
        :target: https://pypi.python.org/pypi/pip-chill

.. image:: https://img.shields.io/travis/rbanffy/pip-chill.svg
        :target: https://travis-ci.org/rbanffy/pip-chill

.. image:: https://readthedocs.org/projects/pip-chill/badge/?version=latest
        :target: https://pip-chill.readthedocs.io/en/latest/?badge=latest
        :alt: Documentation Status

.. image:: https://pyup.io/repos/github/rbanffy/pip-chill/shield.svg
     :target: https://pyup.io/repos/github/rbanffy/pip-chill/
     :alt: Updates

.. image:: https://api.codacy.com/project/badge/Grade/1100f4243bb54a279a3ee6458847b4a7
   :target: https://app.codacy.com/app/rbanffy/pip-chill?utm_source=github.com&utm_medium=referral&utm_content=rbanffy/pip-chill&utm_campaign=Badge_Grade_Dashboard
   :alt: Codacy Badge

Like `pip freeze` but lists only the packages that are not
dependencies of installed packages.


* Free software: GNU General Public License v3
* Documentation: https://pip-chill.readthedocs.io.


Features
--------

Generates a requirements file without any packages that depend on
other packages in the file.

.. image:: https://raw.githubusercontent.com/wiki/rbanffy/pip-chill/demo.gif
   :alt: How it works

Usage
-----

Suppose you have installed in your virtualenv a couple packages. When
you run `pip freeze`, you'll get a list of all packages installed,
with all dependencies. If one of the packages you installed ceases to
depend on an already installed package, you have to manually remove it
from the list. The list also makes no distinction about the packages
you actually care about and packages your packages care about, making
the requirements file bloated and, ultimately, inaccurate.

On your terminal, run::

 $ pip-chill
 bandit==1.7.0
 bumpversion==0.6.0
 click==7.1.2
 coverage==5.3.1
 flake8==3.8.4
 nose==1.3.7
 pip-chill==1.0.1
 pytest==6.2.1
 ...

Or, if you want it without version numbers::

 $ pip-chill --no-version
 bandit
 bumpversion
 click
 coverage
 flake8
 nose
 pip-chill
 pytest
 ...

Or, if you want it without pip-chill::

 $ pip-chill --no-chill
 bandit==1.7.0
 bumpversion==0.6.0
 click==7.1.2
 coverage==5.3.1
 flake8==3.8.4
 nose==1.3.7
 pytest==6.2.1
 ...

Or, if you want to list package dependencies too::

 $ pip-chill -v
 bandit==1.7.0
 bumpversion==0.6.0
 click==7.1.2
 coverage==5.3.1
 flake8==3.8.4
 nose==1.3.7
 pip-chill==1.0.1
 pytest==6.2.1
 sphinx==3.4.3
 tox==3.21.1
 twine==3.3.0
 watchdog==1.0.2
 # alabaster==0.7.12 # Installed as dependency for sphinx
 # appdirs==1.4.4 # Installed as dependency for virtualenv
 # attrs==20.3.0 # Installed as dependency for pytest
 # babel==2.9.0 # Installed as dependency for sphinx
 # bleach==3.2.1 # Installed as dependency for readme-renderer
 # bump2version==1.0.1 # Installed as dependency for bumpversion
 # certifi==2020.12.5 # Installed as dependency for requests
 # chardet==4.0.0 # Installed as dependency for requests
 # colorama==0.4.4 # Installed as dependency for twine
 # distlib==0.3.1 # Installed as dependency for virtualenv
 # docutils==0.16 # Installed as dependency for readme-renderer, sphinx
 # filelock==3.0.12 # Installed as dependency for tox, virtualenv
 # gitdb==4.0.5 # Installed as dependency for gitpython
 ...

Credits
-------

This package was created with Cookiecutter_ and the
`audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
