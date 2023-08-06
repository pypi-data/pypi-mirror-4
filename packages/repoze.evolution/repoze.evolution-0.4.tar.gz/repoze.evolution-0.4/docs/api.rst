API Documentation for repoze.evolution
======================================

.. _api_module:

:mod:`repoze.evolution`
-----------------------

.. automodule:: repoze.evolution

  .. autofunction:: evolve_to_latest


Interfaces
----------

This is the interface which must be supported by ``manager`` objects
which are passed to e.g. ``evolve_to_latest``.

.. code-block:: python

    class repoze.evolution.IEvolutionManager(Interface):
        def get_sw_version():
            """ Return the software version of the managed package """

        def get_db_version():
            """ Return the database version of the managed package """

        def evolve_to(version):
            """ Perform work to evolve to the integer ``version``.  This
            method is also responsible for setting the db version after a
            success."""

The ``repoze.evolution.ZODBEvolutionManager`` implements this interface.
