Documentation for :mod:`repoze.evolution`
=========================================

:mod:`repoze.evolution` is a package which allows you to keep
persistent data structures (data in a relational database, on the
filesystem, in a persistent object store, etc) in sync with changes
made to software.  It does so by allowing you to create and use a
package full of monotonically named ``evolve`` scripts which modify
the data; each script brings the data up to some standard of a
software version.  It includes a "manager" implementation for ZODB,
and an interface which allows you to implement different types of
managers for different persistent data stores.

.. toctree::
   :maxdepth: 2

   narr.rst
   api.rst
   changes.rst

Indices and tables
------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
