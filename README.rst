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
 asciitree==0.3.1
 autopep8==1.2.4
 beautifulsoup4==4.4.0
 bleach==1.4.1
 cookiecutter==1.4.0
 coverage==3.7.1
 django-argonauts==1.0.1
 ...

Or, if you want it without version numbers::

 $ pip-chill --no-version
 asciitree
 autopep8
 beautifulsoup4
 bleach
 cookiecutter
 coverage
 django-argonauts
 ...

Or, if you want to list package dependencies too::

 $ pip-chill -v
 asciitree==0.3.1
 autopep8==1.2.4
 beautifulsoup4==4.4.0
 bleach==1.4.1
 cookiecutter==1.4.0
 coverage==3.7.1
 django-argonauts==1.0.1
 # arrow==0.10.0 # Installed as dependency for jinja2-time
 # binaryornot==0.4.4 # Installed as dependency for cookiecutter
 # chardet==3.0.4 # Installed as dependency for binaryornot
 # click==6.7 # Installed as dependency for cookiecutter
 # django==1.11.5 # Installed as dependency for django-argonauts
 # future==0.16.0 # Installed as dependency for cookiecutter
 # html5lib==0.999999999 # Installed as dependency for bleach
 # jinja2==2.9.6 # Installed as dependency for jinja2-time, cookiecutter
 # jinja2-time==0.2.0 # Installed as dependency for cookiecutter
 # markupsafe==1.0 # Installed as dependency for jinja2
 # pep8==1.7.0 # Installed as dependency for autopep8
 # poyo==0.4.1 # Installed as dependency for cookiecutter
 # python-dateutil==2.6.1 # Installed as dependency for arrow
 # pytz==2017.2 # Installed as dependency for django
 # six==1.11.0 # Installed as dependency for python-dateutil, html5lib, bleach
 # webencodings==0.5.1 # Installed as dependency for html5lib
 # whichcraft==0.4.1 # Installed as dependency for cookiecutter
 ...

Credits
-------

This package was created with Cookiecutter_ and the
`audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
