=======
History
=======

1.0.3 (...)
------------------
* Add dependency on `setuptools` for python >= 3.12 to get access to `pkg_resources`.

1.0.2 (2023-04-15)
------------------
* Sort dependencies alphabetically in --verbose
* Use `ssort` to topologically sort code
* Update 3.11-dev to 3.11 on TravisCI
* Remove support for Python 3.5 and 3.6
* Update README.rst with --no-chill switch
* Bump version to 1.0.2

1.0.1 (2021-01-18)
------------------

* Add `no-chill` option so that pip-chill is not shown as installed
* Do Linux tests on Focal where possible (2.7 and 3.7 on ppc64le and s390x, 2.7 on arm64 run Bionic)
* Fix wrong URLs in CONTRIBUTING.rst
* Add 3.7, 3.8, 3.9 to ppc64le and s390x, 3.10-dev to Linux, macOS
* Rename nightly as 3.10-dev
* Add explicit amd64 arch to amd64
* Fix failing flake8 test
* Bump version to 1.0.1

1.0.0 (2020-02-29)
------------------

* Remove dependency on Click (stay 100% within stdlib)
* Add 3.8 tests for Tox
* Add new tests
* Add arm, ppc64le, and s390x to architectures being tested
* Bump version to 1.0.0

0.1.9 (2019-07-23)
------------------

* New `-a` shortcut for `--all`
* Internal fixes - use assert methods in tests, improve markdown.
* Testing improvements (using TravisCI matrix, new base image, etc)
* Small documentation improvements

0.1.8 (2018-08-20)
------------------

* Fixes, compatibility with Python 2.7, 3.6, 3.7

0.1.7 (2018-01-22)
------------------

* Added a verbose command-line switch (fixed #3)

0.1.6 (2016-11-23)
------------------

* Added pkg-resources to packages not shown by default.

0.1.5 (2016-11-05)
------------------

* Added an --all switch.
* Do not show wheel and setuptools unless --all is invoked.

0.1.4 (2016-11-05)
------------------

* Better testing, more of the cookiecutter infrastructure enabled.

0.1.3 (2016-10-06)
------------------

* Added a --no-version switch.


0.1.0 (2016-10-03)
------------------

* First release on PyPI.
