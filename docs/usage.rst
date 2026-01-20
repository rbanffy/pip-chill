=====
Usage
=====

PIP Chill can be used both as a command-line tool and as a Python library.

Command Line Usage
------------------

Basic usage - list top-level packages::

    $ pip-chill
    package1==1.0.0
    package2==2.1.0
    pip-chill==1.0.5

List packages without version numbers::

    $ pip-chill --no-version
    package1
    package2
    pip-chill

Exclude pip-chill from the output::

    $ pip-chill --no-chill
    package1==1.0.0
    package2==2.1.0

Show all packages including dependencies (with dependencies commented out)::

    $ pip-chill --verbose
    package1==1.0.0
    package2==2.1.0
    pip-chill==1.0.5
    # dependency1==0.1.0 # Installed as dependency for package1
    # dependency2==1.2.0 # Installed as dependency for package2

Show all packages without filtering (equivalent to ``pip freeze`` but sorted)::

    $ pip-chill --all
    package1==1.0.0
    package2==2.1.0
    pip-chill==1.0.5
    dependency1==0.1.0
    dependency2==1.2.0

Python API Usage
----------------

Import and use the ``chill`` function::

    >>> import pip_chill
    >>> packages, dependencies = pip_chill.chill()
    >>> for pkg in packages:
    ...     print(pkg)
    package1==1.0.0
    package2==2.1.0
    pip-chill==1.0.5

Get packages without version numbers::

    >>> packages, dependencies = pip_chill.chill(no_version=True)
    >>> for pkg in packages:
    ...     print(pkg)
    package1
    package2
    pip-chill

Include dependencies in verbose mode::

    >>> packages, dependencies = pip_chill.chill(verbose=True)
    >>> for pkg in packages + dependencies:
    ...     print(pkg)
    package1==1.0.0
    package2==2.1.0
    pip-chill==1.0.5
    # dependency1==0.1.0 # Installed as dependency for package1

Show all packages without filtering::

    >>> packages, dependencies = pip_chill.chill(show_all=True)
    >>> for pkg in packages:
    ...     print(pkg)
    package1==1.0.0
    package2==2.1.0
    pip-chill==1.0.5
    dependency1==0.1.0
    dependency2==1.2.0
