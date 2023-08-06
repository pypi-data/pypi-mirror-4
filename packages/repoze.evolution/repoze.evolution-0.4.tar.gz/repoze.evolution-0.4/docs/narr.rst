Using :mod:`repoze.evolution`
=============================

Using the ZODBEvolutionManager
------------------------------

:mod:`repoze.evolution` contains an implementation of an evolution
manager named ``ZODBEvolutionManager``.  You instantiate a
``ZODBEvolutionManager`` like so::

  from my.package import get_persistent_object
  from repoze.evolution import ZODBEvolutionManager
  persistent_object = get_persistent_object()
  context = persistent_object
  manager=ZODBEvolutionManager(context, evolve_packagename='my.package.evolve',
                               sw_version=2)

The above code initializes a ZODB evolution manager.  The``context``
is an object which must inherit from ``persistent.Persistent`` that
will be passed in to each evolution script's evolve method.
``evolve_packagename`` is the Python dotted package name of a package
which contains evolution scripts.  ``sw_version`` is the current
software version of the software represented by this manager.

In the above example, if the database has no version already set on it, the
evolution manager will not attempt to construe what version it should consider
the database to be.  To specify the version the evolution manager should
consider any unversioned database to be, pass a value for the optional fourth
argument, ``initial_db_version``::

  manager=ZODBEvolutionManager(context, evolve_packagename='my.package.evolve',
                               sw_version=2, initial_db_version=0)

In general, when creating a new instance of an application you will need to
bootstrap your database in some way.  At this time, you probably also want to
set the version of your database to the software version.  To do this, use the
``set_db_version()`` method of IEvolutionManager()::

  manager=ZODBEvolutionManager(context, evolve_packagename='my.package.evolve',
                               sw_version=2)
  manager.set_db_version(2)

To provide evolution steps in a package, create the package, and put
modules in it named "evolve<N>.py" where N represents the software
version: N must be >= 1 (0 represents the initial state).  For
example, if you place the following script into the
``my.package.evolve`` package as ``evolve1.py``, when evolution is
run, it will evolve the database to generation #1.

.. code-block:: python
   :linenos:

   def evolve(context):
      context.evolved = 1

After this evolution step is run, the ZODB database will be marked as
"at generation 1" (by mutating a dictionary stored in its root).  Add
further scripts and change the ``sw_version`` of the manager to evolve
further.  The above script is just an example; setting "evolved" on
the context is not necessary; evolve scripts should do arbitrary
things to adjust database data structures to match the code software
version.

Evolution steps are run when the ``evolve_to_latest`` function is used
with an appropriate manager object.
