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
import unittest

_marker = object()

class ZODBEvolutionManagerTests(unittest.TestCase):

    def _getTargetClass(self):
        from repoze.evolution import ZODBEvolutionManager
        return ZODBEvolutionManager

    def _makeOne(self, root=None, sw_version=None, initial_db_version=None,
                 txn=_marker):
        klass = self._getTargetClass()
        context = DummyPersistent(root)
        if txn is _marker:
            txn = DummyTransaction()
        manager = klass(context, 'repoze.evolution.tests.fixtureapp.evolve',
                        sw_version, initial_db_version, txn)
        manager.transaction = txn
        return manager

    def test_verify_class_conforms_to_IEvolutionManager(self):
        from repoze.evolution.interfaces import IEvolutionManager
        from zope.interface.verify import verifyClass
        verifyClass(IEvolutionManager, self._getTargetClass())

    def test_verify_instance_conforms_to_IEvolutionManager(self):
        from repoze.evolution.interfaces import IEvolutionManager
        from zope.interface.verify import verifyObject
        verifyObject(IEvolutionManager, self._makeOne())

    def test_root_property(self):
        klass = self._getTargetClass()
        root = {}
        context = DummyPersistent(root)
        manager = klass(context, 'nonesuch', 42)
        self.failUnless(manager.root is root)

    def test_get_sw_version(self):
        klass = self._getTargetClass()
        root = {}
        context = DummyPersistent(root)
        manager = klass(context, 'nonesuch', 42)
        self.assertEqual(manager.get_sw_version(), 42)

    def test_get_db_version_missing_from_root_uses_initial(self):
        klass = self._getTargetClass()
        root = {}
        context = DummyPersistent(root)
        manager = klass(context, 'nonesuch', 42, 22)
        self.assertEqual(manager.get_db_version(), 22)

    def test_get_db_version_extant_in_root(self):
        klass = self._getTargetClass()
        root = {'repoze.evolution': {'extant':11}}
        context = DummyPersistent(root)
        manager = klass(context, 'extant', 42, 22)
        self.assertEqual(manager.get_db_version(), 11)

    def test_get_db_version_missing_from_root_uses_initial_alt_key(self):
        klass = self._getTargetClass()
        root = {}
        context = DummyPersistent(root)
        manager = klass(context, 'nonesuch', 42, 22)
        manager.key = 'alternate'
        self.assertEqual(manager.get_db_version(), 22)

    def test_get_db_version_extant_in_root_alt_key(self):
        klass = self._getTargetClass()
        root = {'repoze.evolution': {'extant':11},
                'alternate': {'extant':33},
               }
        context = DummyPersistent(root)
        manager = klass(context, 'extant', 42, 22)
        manager.key = 'alternate'
        self.assertEqual(manager.get_db_version(), 33)

    def test_evolve_to_no_key_in_root(self):
        root = {}
        txn = DummyTransaction()
        manager = self._makeOne(root, 1, 0, txn)

        manager.evolve_to(1)

        self.assertEqual(manager.context.evolved, 1)
        self.assertEqual(txn.committed, 1)
        reg = root['repoze.evolution']
        self.assertEqual(reg['repoze.evolution.tests.fixtureapp.evolve'], 1)

    def test_evolve_to_w_key_in_root(self):
        root = {'repoze.evolution':
                {'repoze.evolution.tests.fixtureapp.evolve':1}}
        txn = DummyTransaction()
        manager = self._makeOne(root, 2, None, txn)

        manager.evolve_to(2)

        self.assertEqual(manager.context.evolved, 2)
        self.assertEqual(txn.committed, 1)
        reg = root['repoze.evolution']
        self.assertEqual(reg['repoze.evolution.tests.fixtureapp.evolve'], 2)

    def test_evolve_to_w_key_in_root_txn_None(self):
        root = {'repoze.evolution':
                {'repoze.evolution.tests.fixtureapp.evolve':1}}
        manager = self._makeOne(root, 2, None, None)

        manager.evolve_to(2)

        self.assertEqual(manager.context.evolved, 2)
        reg = root['repoze.evolution']
        self.assertEqual(reg['repoze.evolution.tests.fixtureapp.evolve'], 2)

    def test_evolve_to_script_raises(self):
        root = {'repoze.evolution':
                {'repoze.evolution.tests.fixtureapp.evolve':2}}
        txn = DummyTransaction()
        manager = self._makeOne(root, 3, None, txn)

        self.assertRaises(ValueError, manager.evolve_to, 3)

        self.assertEqual(txn.committed, 0)
        reg = root['repoze.evolution']
        self.assertEqual(reg['repoze.evolution.tests.fixtureapp.evolve'], 2)

    def test_set_db_version_missing_from_root_uses_initial(self):
        klass = self._getTargetClass()
        root = {}
        context = DummyPersistent(root)
        manager = klass(context, 'extant', 42, 33)
        manager.set_db_version(22)
        self.assertEqual(root['repoze.evolution']['extant'], 22)

    def test_set_db_version_extant_in_root_wo_transaction(self):
        klass = self._getTargetClass()
        root = {'repoze.evolution': {'extant':11}}
        context = DummyPersistent(root)
        manager = klass(context, 'extant', 42, 33, None)
        manager.set_db_version(22)
        self.assertEqual(root['repoze.evolution']['extant'], 22)

    def test_set_db_version_extant_in_root_w_txn_wo_commit(self):
        klass = self._getTargetClass()
        root = {'repoze.evolution': {'extant':11}}
        context = DummyPersistent(root)
        txn = DummyTransaction()
        manager = klass(context, 'extant', 42, 33, txn)
        manager.set_db_version(22, commit=False)
        self.assertEqual(root['repoze.evolution']['extant'], 22)
        self.assertEqual(txn.committed, 0)

    def test_set_db_version_extant_in_root_w_txn_w_commit(self):
        klass = self._getTargetClass()
        root = {'repoze.evolution': {'extant':11}}
        context = DummyPersistent(root)
        txn = DummyTransaction()
        manager = klass(context, 'extant', 42, 33, txn)
        manager.set_db_version(22, commit=True)
        self.assertEqual(root['repoze.evolution']['extant'], 22)
        self.assertEqual(txn.committed, 1)

    def test_set_db_version_missing_from_root_uses_initial_alt_key(self):
        klass = self._getTargetClass()
        root = {}
        context = DummyPersistent(root)
        txn = DummyTransaction()
        manager = klass(context, 'extant', 42, 22, txn)
        manager.key = 'alternate'
        manager.set_db_version(22)
        self.assertEqual(root['alternate']['extant'], 22)
        self.assertEqual(txn.committed, 1)

    def test_set_db_version_extant_in_root_alt_key(self):
        klass = self._getTargetClass()
        root = {'repoze.evolution': {'extant':11},
                'alternate': {'extant':33},
               }
        context = DummyPersistent(root)
        txn = DummyTransaction()
        manager = klass(context, 'extant', 42, 22, txn)
        manager.key = 'alternate'
        manager.set_db_version(22)
        self.assertEqual(root['alternate']['extant'], 22)
        self.assertEqual(txn.committed, 1)


class Test_evolve_to_latest(unittest.TestCase):

    def _callFUT(self, *args, **kw):
        from repoze.evolution import evolve_to_latest
        return evolve_to_latest(*args, **kw)

    def test_swver_not_integer(self):
        manager = DummyManager('1', 1)
        self.assertRaises(ValueError, self._callFUT, manager)

    def test_no_db_version(self):
        manager = DummyManager(1, None)
        self.assertRaises(ValueError, self._callFUT, manager)

    def test_dbver_not_integer(self):
        manager = DummyManager(1, '1')
        self.assertRaises(ValueError, self._callFUT, manager)

    def test_dbver_lt_swver(self):
        manager = DummyManager(1, 0)

        version = self._callFUT(manager)

        self.assertEqual(version, 1)
        self.assertEqual(manager._evolved_to, [1])

    def test_dbver_gt_swver(self):
        manager = DummyManager(1, 2)

        version = self._callFUT(manager)

        self.assertEqual(version, 2)
        self.assertEqual(manager._evolved_to, [])

    def test_dbver_eq_swver(self):
        manager = DummyManager(1, 1)

        version = self._callFUT(manager)

        self.assertEqual(version, 1)
        self.assertEqual(manager._evolved_to, [])


class Dummy(object):
    pass


class DummyPersistent(object):
    evolved = None
    def __init__(self, root):
        self._p_jar = Dummy()
        self._p_jar.root = lambda *arg: root
        self.error = False


class DummyTransaction(object):
    committed = 0
    begun = 0
    def commit(self):
        self.committed = self.committed + 1

    def begin(self):
        self.begun = self.begun + 1


class DummyManager(object):

    def __init__(self, sw_version, db_version):
        self._sw_version = sw_version
        self._db_version = db_version
        self._evolved_to = []

    def get_sw_version(self):
        return self._sw_version

    def get_db_version(self):
        return self._db_version

    def evolve_to(self, version):
        self._evolved_to.append(version)
