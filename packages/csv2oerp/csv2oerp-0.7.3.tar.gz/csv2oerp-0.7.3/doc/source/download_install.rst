.. _download-install:

Download and install instructions
=================================

Python Package Index (PyPI)
---------------------------

You can install `csv2oerp` with the `easy_install` tool::

    $ easy_install csv2oerp

Or with `pip`::

    $ pip install csv2oerp

An alternative way is to download the tarball from
`Python Package Index <http://pypi.python.org/pypi/csv2oerp/>`_ page,
and install manually (replace `X.Y.Z` accordingly)::

    $ wget http://pypi.python.org/packages/source/C/csv2oerp/csv2oerp-X.Y.Z.tar.gz
    $ tar xzvf csv2oerp-X.Y.Z.tar.gz
    $ cd csv2oerp-X.Y.Z
    $ python setup.py install

No dependency is required for basic use. Otherwize, see sections `Dependancies`

Source code
-----------

The project is hosted on `Bitbucket <https://bitbucket.org/StefMangin/python-csv2oerp>`_.
To get the current development branch (the ``trunk``), just type::

    $ hg clone https://StefMangin@bitbucket.org/StefMangin/python-csv2oerp

For the last version of a stable branch (replace `X.Y` accordingly)::

    $ hg clone https://StefMangin@bitbucket.org/StefMangin/python-csv2oerp-X.Y

.. Run tests
.. ---------
.. 
.. .. versionadded:: 0.4.0
.. 
.. To run unit tests from the project directory, run the following command::
.. 
..     PYTHONPATH=. ./tests/runtests.py --help
.. 
.. Then, set your parameters in order to indicate the `OpenERP` server on which
.. you want to perform the tests, for instance::
.. 
..     PYTHONPATH=. ./tests/runtests.py --create_db --server 192.168.1.4
.. 
.. The name of the database created is ``oerplib-test`` by default.
