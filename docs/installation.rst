.. highlight:: shell

============
Installation
============


Stable release
--------------

To install PIP Chill, run this command in your terminal:

.. code-block:: console

    $ pip install pip_chill

This is the preferred method to install PIP Chill, as it will always install the most recent stable release.

If you don't have `pip`_ installed, this `Python installation guide`_ can guide
you through the process.

.. _pip: https://pip.pypa.io
.. _Python installation guide: http://docs.python-guide.org/en/latest/starting/installation/

From sources
------------

The sources for PIP Chill can be downloaded from the `GitHub repo`_.

You can either clone the public repository:

.. code-block:: console

    $ git clone https://github.com/rbanffy/pip-chill

Or download the `tarball`_:

.. code-block:: console

    $ curl -OL https://github.com/rbanffy/pip-chill/tarball/master

Once you have a copy of the source, you can install it in a virtual environment:

.. code-block:: console

    $ python -m venv .venv
    $ source .venv/bin/activate   # On Windows: .venv\Scripts\activate
    $ pip install -e .

This will install PIP Chill in “editable” mode, so changes to the source are immediately reflected.

Alternatively, if you prefer using the Makefile:

.. code-block:: console

    $ make install

.. _GitHub repo: https://github.com/rbanffy/pip-chill
.. _tarball: https://github.com/rbanffy/pip-chill/tarball/master
