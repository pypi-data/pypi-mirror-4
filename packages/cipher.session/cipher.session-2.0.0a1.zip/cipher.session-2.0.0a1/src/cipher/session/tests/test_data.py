#tests taken from repoze.session

import unittest


class TestSessionData(unittest.TestCase):
    def _getTargetClass(self):
        from cipher.session.session import SessionData
        return SessionData

    def _makeOne(self, data=None):
        return self._getTargetClass()(data)

    def test_instance_implements_ISessionData(self):
        from zope.interface.verify import verifyObject
        from repoze.session.interfaces import ISessionData
        verifyObject(ISessionData, self._makeOne())

    def test_class_implements_ISessionData(self):
        from zope.interface.verify import verifyClass
        from repoze.session.interfaces import ISessionData
        verifyClass(ISessionData, self._getTargetClass())

    def test_p_resolveConflict_different_lm_different_container(self):
        from ZODB.POSException import ConflictError
        sdo = self._makeOne()
        old = {}
        committed = {'_lm':1, '_container':1}
        new       = {'_lm':2, '_container':2}
        self.assertRaises(ConflictError, sdo._p_resolveConflict, old,
                          committed, new)

    def test_p_resolveConflict_different_lm_same_container(self):
        sdo = self._makeOne()
        old = {}
        committed = {'_lm':1, '_container':1, '_la':1, '_iv':1}
        new       = {'_lm':2, '_container':1, '_la':1, '_iv':1}
        result = sdo._p_resolveConflict(old, committed, new)
        self.assertEqual(
            result,
            {'_la': 1, '_container': 1, '_lm': 2, '_iv': True}
            )

    def test_p_resolveConflict_same_lm(self):
        sdo = self._makeOne()
        old = {}
        committed = {'_lm':1, '_container':1}
        new       = {'_lm':1, '_container':1}
        result = sdo._p_resolveConflict(old, committed, new)
        self.assertEqual(result, {'_container': 1, '_lm': 1})


    def test_p_resolveConflict_different_lm_different_data(self):
        from ZODB.POSException import ConflictError
        sdo = self._makeOne()
        old = {}
        committed = {'_lm':1, 'data':1}
        new       = {'_lm':2, 'data':2}
        self.assertRaises(ConflictError, sdo._p_resolveConflict, old,
                          committed, new)

    def test_p_resolveConflict_different_lm_same_data(self):
        sdo = self._makeOne()
        old = {}
        committed = {'_lm':1, 'data':1, '_la':1, '_iv':1}
        new       = {'_lm':2, 'data':1, '_la':1, '_iv':1}
        result = sdo._p_resolveConflict(old, committed, new)
        self.assertEqual(
            result,
            {'_la': 1, 'data': 1, '_lm': 2, '_iv': True}
            )

    def test_p_resolveConflict_same_lm_data(self):
        sdo = self._makeOne()
        old = {}
        committed = {'_lm':1, 'data':1}
        new       = {'_lm':1, 'data':1}
        result = sdo._p_resolveConflict(old, committed, new)
        self.assertEqual(result, {'data': 1, '_lm': 1})


    def test_p_resolveConflict_different_lm_different_persistent(self):
        from ZODB.POSException import ConflictError
        from ZODB.ConflictResolution import PersistentReference

        ref1 = PersistentReference(b'my_oid')
        ref2 = PersistentReference((b'another_oid', 'my_class'))

        sdo = self._makeOne()
        old = {}
        committed = {'_lm':1, 'data':ref1}
        new       = {'_lm':2, 'data':ref2}
        self.assertRaises(ConflictError, sdo._p_resolveConflict, old,
                          committed, new)
