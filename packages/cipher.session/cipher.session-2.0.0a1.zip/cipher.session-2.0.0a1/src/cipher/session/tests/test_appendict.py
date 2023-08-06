""" Unit tests for AppendOnlyDict taken from Products.faster.appendict
"""
import unittest
from cipher.session._compat import PY3

class ApppendOnlyDictTests(unittest.TestCase):

    def _getTargetClass(self):
        from cipher.session.session import AppendOnlyDict
        return AppendOnlyDict

    def _makeOne(self, *args, **kw):
        return self._getTargetClass()(*args, **kw)

    def test___setitem__new_key_succeeds(self):
        aod = self._makeOne()
        self.assertEqual(len(aod.keys()), 0)
        aod['somekey'] = 'somevalue'
        self.assertEqual(len(aod.keys()), 1)
        self.failUnless('somekey' in aod)

    def test___setitem__existing_key_raises_TypeError(self):
        aod = self._makeOne()
        aod['somekey'] = 'somevalue'
        self.assertRaises(TypeError, aod.__setitem__, 'somekey', 'anyvalue')

    def test___delitem__non_existing_key_raises_KeyError(self):
        aod = self._makeOne()
        self.assertRaises(KeyError, aod.__delitem__, 'somekey')

    def test___setitem__dict_value_raises_TypeError(self):
        aod = self._makeOne()
        mutable = {'a': 'A'}
        self.assertRaises(TypeError, aod.__setitem__, 'somekey', mutable)

    def test___setitem__list_value_raises_TypeError(self):
        aod = self._makeOne()
        mutable = ['A', 'B']
        self.assertRaises(TypeError, aod.__setitem__, 'somekey', mutable)

    def test___setitem__non_perssistent_inst_value_raises_TypeError(self):
        aod = self._makeOne()
        class Mutable:
            pass
        mutable = Mutable()
        if not PY3:
            self.assertRaises(TypeError, aod.__setitem__, 'somekey', mutable)

    def test___delitem__existing_key_raises_TypeError(self):
        aod = self._makeOne()
        aod['somekey'] = 'somevalue'
        self.assertRaises(TypeError, aod.__delitem__, 'somekey')

    def test__p_resolveConflict_wo_collistions(self):
        old = {'a': 'A', 'b': 'B'}
        committed = old.copy()
        committed['c'] = 'C'
        new = old.copy()
        new['d'] = 'D'

        merged = old.copy()
        merged.update(committed)
        merged.update(new)

        aod = self._makeOne()
        resolved = aod._p_resolveConflict(old, committed, new)
        self.assertEqual(resolved, merged)

    def test__p_resolveConflict_with_committed_clear(self):
        from ZODB.POSException import ConflictError

        old = {'a': 'A', 'b': 'B'}
        committed = {}
        new = old.copy()
        new['c'] = 'C'
        new['d'] = 'D'

        aod = self._makeOne()
        self.assertRaises(ConflictError,
                          aod._p_resolveConflict, old, committed, new)

    def test__p_resolveConflict_with_new_clear(self):
        from ZODB.POSException import ConflictError

        old = {'a': 'A', 'b': 'B'}
        committed = old.copy()
        committed['c'] = 'C'
        committed['d'] = 'D'
        new = {}

        aod = self._makeOne()
        self.assertRaises(ConflictError,
                          aod._p_resolveConflict, old, committed, new)

    def test__p_resolveConflict_with_collistions(self):
        from ZODB.POSException import ConflictError

        old = {'a': 'A', 'b': 'B'}
        committed = old.copy()
        committed['c'] = 'C'
        new = old.copy()
        new['c'] = 'ccc'
        new['d'] = 'D'
        aod = self._makeOne()

        self.assertRaises(ConflictError,
                          aod._p_resolveConflict, old, committed, new)


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(ApppendOnlyDictTests),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
