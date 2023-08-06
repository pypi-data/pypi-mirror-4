##############################################################################
#
# Copyright (c) 2008-2011 Agendaless Consulting and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the BSD-like license at
# http://www.repoze.org/LICENSE.txt.  A copy of the license should accompany
# this distribution.  THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL
# EXPRESS OR IMPLIED WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO,
# THE IMPLIED WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND
# FITNESS FOR A PARTICULAR PURPOSE
#
##############################################################################

from pkg_resources import EntryPoint
from zope.interface import implementer

from repoze.evolution.interfaces import IEvolutionManager

_marker = object()


@implementer(IEvolutionManager)
class ZODBEvolutionManager:
    key = 'repoze.evolution'
    def __init__(self,
                 context,
                 evolve_packagename,
                 sw_version,
                 initial_db_version=None,
                 txn=_marker,
                ):
        """ Initialize a ZODB evolution manager.  ``context`` is an
        object which must inherit from ``persistent.Persistent`` that
        will be passed in to each evolution step.  evolve_packagename
        is the Python dotted package name of a package which contains
        evolution scripts.  ``sw_version`` is the current software
        version of the software represented by this manager.
        ``initial_db_version`` indicates the presumed version of a database
        which doesn't already have a version set.  If not supplied or is set
        to ``None``, the evolution manager will not attempt to construe the
        version of a an unversioned db. ``dry_run``, if True, tells the
        manager not to commit any transactions.
        """
        if txn is _marker:
            import transaction
            self.transaction = transaction
        else:
            self.transaction = txn
        self.context = context
        self.package_name = evolve_packagename
        self.sw_version = sw_version
        self.initial_db_version = initial_db_version

    @property
    def root(self):
        return self.context._p_jar.root()

    def get_sw_version(self):
        return self.sw_version

    def get_db_version(self):
        registry = self.root.setdefault(self.key, {})
        db_version = registry.get(self.package_name)
        if db_version is None:
            return self.initial_db_version
        return db_version

    def evolve_to(self, version):
        scriptname = '%s.evolve%s' % (self.package_name, version)
        evmodule = EntryPoint.parse('x=%s' % scriptname).load(False)
        if self.transaction is not None:
            self.transaction.begin()
        evmodule.evolve(self.context)
        self.set_db_version(version, commit=False)
        if self.transaction is not None:
            self.transaction.commit()

    def set_db_version(self, version, commit=True):
        registry = self.root.setdefault(self.key, {})
        registry[self.package_name] = version
        self.root[self.key] = registry
        if commit and self.transaction is not None:
            self.transaction.commit()

    # b/w compatibility
    _set_db_version = set_db_version


def evolve_to_latest(manager):
    """ Evolve the database to the latest software version using the
    ``manager`` object.  """
    db_version = manager.get_db_version()
    sw_version = manager.get_sw_version()
    if not isinstance(sw_version, int):
        raise ValueError('software version %s is not an integer' %
                         sw_version)
    if db_version is None:
        raise ValueError('database version has not been set and no initial '
                         'value has been provided.')
    if not isinstance(db_version, int):
        raise ValueError('database version %s is not an integer' %
                         db_version)
    if db_version < sw_version:
        for version in range(db_version+1, sw_version+1):
            manager.evolve_to(version)
        return version
    return db_version
