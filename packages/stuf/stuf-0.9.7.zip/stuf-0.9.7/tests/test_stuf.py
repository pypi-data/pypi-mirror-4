# -*- coding: utf-8 -*-
'''test stuf'''

from stuf.six import unittest


class Base(object):

    @property
    def _makeone(self):
        return self._impone(test1='test1', test2='test2', test3=dict(e=1))

    def setUp(self):
        self.stuf = self._makeone

    def test__getattr__(self):
        self.assertEqual(self.stuf.test1, 'test1')
        self.assertEqual(self.stuf.test2, 'test2')
        self.assertEqual(self.stuf.test3.e, 1)

    def test__getitem__(self):
        self.assertEqual(self.stuf['test1'], 'test1')
        self.assertEqual(self.stuf['test2'], 'test2')
        self.assertEqual(self.stuf['test3']['e'], 1)

    def test_get(self):
        self.assertEqual(self.stuf.get('test1'), 'test1')
        self.assertEqual(self.stuf.get('test2'), 'test2')
        self.assertIsNone(self.stuf.get('test4'), 'test4')
        self.assertEqual(self.stuf.get('test3').get('e'), 1)
        self.assertIsNone(self.stuf.get('test3').get('r'))

    def test__setattr__(self):
        self.stuf.max = 3
        self.stuf.test1 = 'test1again'
        self.stuf.test2 = 'test2again'
        self.stuf.test3.e = 5
        self.assertEqual(self.stuf.max, 3)
        self.assertEqual(self.stuf.test1, 'test1again')
        self.assertEqual(self.stuf.test2, 'test2again')
        self.assertEqual(self.stuf.test3.e, 5)

    def test__setitem__(self):
        self.stuf['max'] = 3
        self.stuf['test1'] = 'test1again'
        self.stuf['test2'] = 'test2again'
        self.stuf['test3']['e'] = 5
        self.assertEqual(self.stuf['max'], 3)
        self.assertEqual(self.stuf['test1'], 'test1again')
        self.assertEqual(self.stuf['test2'], 'test2again')
        self.assertEqual(self.stuf['test3']['e'], 5)

    def test__delattr__(self):
        del self.stuf.test1
        del self.stuf.test2
        del self.stuf.test3.e
        self.assertEqual(len(self.stuf.test3), 0)
        del self.stuf.test3
        self.assertRaises(AttributeError, lambda: delattr(self.stuf, 'test4'))
        self.assertEqual(len(self.stuf), 0)
        self.assertRaises(AttributeError, lambda: self.stuf.test1)
        self.assertRaises(AttributeError, lambda: self.stuf.test2)
        self.assertRaises(AttributeError, lambda: self.stuf.test3)
        self.assertRaises(AttributeError, lambda: self.stuf.test3.e)

    def test__delitem__(self):
        del self.stuf['test1']
        del self.stuf['test2']
        del self.stuf['test3']['e']
        self.assertNotIn('e', self.stuf['test3'])
        self.assertTrue(len(self.stuf['test3']) == 0)
        del self.stuf['test3']
        self.assertTrue(len(self.stuf) == 0)
        self.assertNotIn('test1', self.stuf)
        self.assertNotIn('test2', self.stuf)
        self.assertNotIn('test3', self.stuf)

    def test__cmp__(self):
        tstuff = self._makeone
        self.assertEqual(self.stuf, tstuff)

    def test__len__(self):
        self.assertEqual(len(self.stuf), 3)
        self.assertEqual(len(self.stuf.test3), 1)

    def test_repr(self):
        from stuf.six import strings
        self.assertIsInstance(repr(self._makeone), strings)
        self.assertIsInstance(repr(self.stuf), strings)

    def test_items(self):
        slist = list(self.stuf.items())
        self.assertIn(('test1', 'test1'), slist)
        self.assertIn(('test2', 'test2'), slist)
        self.assertIn(('test3', {'e': 1}), slist)

    def test_iteritems(self):
        slist = list(self.stuf.iteritems())
        self.assertIn(('test1', 'test1'), slist)
        self.assertIn(('test2', 'test2'), slist)
        self.assertIn(('test3', {'e': 1}), slist)

    def test_iter(self):
        slist = list(self.stuf)
        slist2 = list(self.stuf.test3)
        self.assertIn('test1', slist)
        self.assertIn('test2', slist)
        self.assertIn('test3', slist)
        self.assertIn('e', slist2)

    def test_iterkeys(self):
        slist = list(self.stuf.iterkeys())
        slist2 = list(self.stuf.test3.iterkeys())
        self.assertIn('test1', slist)
        self.assertIn('test2', slist)
        self.assertIn('test3', slist)
        self.assertIn('e', slist2)

    def test_itervalues(self):
        slist = list(self.stuf.itervalues())
        slist2 = list(self.stuf.test3.itervalues())
        self.assertIn('test1', slist)
        self.assertIn('test2', slist)
        self.assertIn({'e': 1}, slist)
        self.assertIn(1, slist2)

    def test_values(self):
        slist1 = self.stuf.test3.values()
        slist2 = self.stuf.values()
        self.assertIn(1, slist1)
        self.assertIn('test1', slist2)
        self.assertIn('test2', slist2)
        self.assertIn({'e': 1}, slist2)

    def test_keys(self):
        slist1 = self.stuf.test3.keys()
        slist2 = self.stuf.keys()
        self.assertIn('e', slist1)
        self.assertIn('test1', slist2)
        self.assertIn('test2', slist2)
        self.assertIn('test3', slist2)

    def test_pickle(self):
        import pickle
        tstuf = self._makeone
        pkle = pickle.dumps(tstuf)
        nstuf = pickle.loads(pkle)
        self.assertIsInstance(nstuf, self._impone)
        self.assertEqual(tstuf, nstuf)

    def test_clear(self):
        self.stuf.test3.clear()
        self.assertEqual(len(self.stuf.test3), 0)
        self.stuf.clear()
        self.assertEqual(len(self.stuf), 0)

    def test_pop(self):
        self.assertEqual(self.stuf.test3.pop('e'), 1)
        self.assertEqual(self.stuf.pop('test1'), 'test1')
        self.assertEqual(self.stuf.pop('test2'), 'test2')
        self.assertEqual(self.stuf.pop('test3'), {})

    def test_copy(self):
        tstuf = self._makeone
        nstuf = tstuf.copy()
        self.assertIsInstance(nstuf, self._impone)
        self.assertIsInstance(tstuf, self._impone)
        self.assertEqual(tstuf, nstuf)

    def test_popitem(self):
        item = self.stuf.popitem()
        self.assertEqual(len(item) + len(self.stuf), 4, item)

    def test_setdefault(self):
        self.assertEqual(self.stuf.test3.setdefault('e', 8), 1)
        self.assertEqual(self.stuf.test3.setdefault('r', 8), 8)
        self.assertEqual(self.stuf.setdefault('test1', 8), 'test1')
        self.assertEqual(self.stuf.setdefault('pow', 8), 8)

    def test_update(self):
        tstuff = self._makeone
        tstuff['test1'] = 3
        tstuff['test2'] = 6
        tstuff['test3'] = dict(f=2)
        self.stuf.update(tstuff)
        self.assertEqual(self.stuf['test1'], 3, self.stuf.items())
        self.assertEqual(self.stuf['test2'], 6)
        self.assertEqual(self.stuf['test3'], dict(f=2), self.stuf)

    def test_nofile(self):
        import sys
        s = self._impone(a=sys.stdout, b=1)
        self.assertEqual(s.a, sys.stdout)
        t = self._impone(a=[sys.stdout], b=1)
        self.assertEqual(t.a, [sys.stdout])


class TestStuf(Base, unittest.TestCase):

    @property
    def _impone(self):
        from stuf import stuf
        return stuf


class TestDefaultStuf(Base, unittest.TestCase):

    @property
    def _impone(self):
        from stuf import defaultstuf
        return defaultstuf

    @property
    def _makeone(self):
        return self._impone(
            list, test1='test1', test2='test2', test3=dict(e=1)
        )

    def test__getattr__(self):
        self.assertEqual(self.stuf.test1, 'test1')
        self.assertEqual(self.stuf.test2, 'test2')
        self.assertEqual(self.stuf.test4, [])
        self.assertEqual(self.stuf.test3.e, 1)
        self.assertEqual(self.stuf.test3.f, [])

    def test__getitem__(self):
        self.assertEqual(self.stuf['test1'], 'test1')
        self.assertEqual(self.stuf['test2'], 'test2')
        self.assertEqual(self.stuf['test4'], [])
        self.assertEqual(self.stuf['test3']['e'], 1)
        self.assertEqual(self.stuf['test3']['f'], [])

    def test__delattr__(self):
        del self.stuf.test1
        del self.stuf.test2
        del self.stuf.test3.e
        self.assertEqual(len(self.stuf.test3), 0)
        del self.stuf.test3
        self.assertEqual(len(self.stuf), 0)
        self.assertEqual(self.stuf.test1, [])
        self.assertEqual(self.stuf.test2, [])
        self.assertEqual(self.stuf.test3, [])
        self.assertRaises(AttributeError, lambda: self.stuf.test3.e)

    def test__delitem__(self):
        del self.stuf['test1']
        del self.stuf['test2']
        del self.stuf['test3']['e']
        self.assertNotIn('e', self.stuf['test3'])
        self.assertEqual(len(self.stuf['test3']), 0)
        self.assertEqual(self.stuf['test3']['e'], [])
        del self.stuf['test3']
        self.assertEqual(len(self.stuf), 0)
        self.assertNotIn('test1', self.stuf)
        self.assertNotIn('test2', self.stuf)
        self.assertNotIn('test3', self.stuf)
        self.assertEqual(self.stuf['test1'], [])
        self.assertEqual(self.stuf['test2'], [])
        self.assertEqual(self.stuf['test3'], [])
        self.assertRaises(TypeError, lambda: self.stuf['test3']['e'])

    def test_clear(self):
        self.stuf.test3.clear()
        self.assertEqual(len(self.stuf.test3), 0)
        self.assertEqual(self.stuf['test3']['e'], [])
        self.stuf.clear()
        self.assertEqual(len(self.stuf), 0)
        self.assertEqual(self.stuf['test1'], [])
        self.assertEqual(self.stuf['test2'], [])
        self.assertEqual(self.stuf['test3'], [])

    def test_nofile(self):
        import sys
        s = self._impone(list, a=sys.stdout, b=1)
        self.assertEqual(s.a, sys.stdout)
        t = self._impone(list, a=[sys.stdout], b=1)
        self.assertEqual(t.a, [sys.stdout])


class TestFixedStuf(Base, unittest.TestCase):

    @property
    def _impone(self):
        from stuf import fixedstuf
        return fixedstuf

    def test__setattr__(self):
        self.assertRaises(AttributeError, lambda: setattr(self.stuf, 'max', 3))
        self.stuf.test1 = 'test1again'
        self.stuf.test2 = 'test2again'
        self.stuf.test3.e = 5
        self.assertRaises(AttributeError, lambda: self.stuf.max)
        self.assertEqual(self.stuf.test1, 'test1again')
        self.assertEqual(self.stuf.test2, 'test2again')
        self.assertEqual(self.stuf.test3.e, 5)

    def test__setitem__(self):
        self.assertRaises(KeyError, lambda: self.stuf.__setitem__('max', 3))
        self.stuf['test1'] = 'test1again'
        self.stuf['test2'] = 'test2again'
        self.stuf['test3']['e'] = 5
        self.assertRaises(KeyError, lambda: self.stuf.__getitem__('max'))
        self.assertEqual(self.stuf['test1'], 'test1again')
        self.assertEqual(self.stuf['test2'], 'test2again')
        self.assertEqual(self.stuf['test3']['e'], 5)

    def test__delattr__(self):
        self.assertRaises(TypeError, lambda: delattr(self.stuf.test1))
        self.assertRaises(TypeError, lambda: delattr(self.stuf.test3.e))

    def test__delitem__(self):
        del self.stuf.test3['e']
        self.assertRaises(KeyError, lambda: self.stuf.test3['e'])
        del self.stuf['test1']
        self.assertRaises(KeyError, lambda: self.stuf['test1'])

    def test_clear(self):
        self.assertRaises(KeyError, lambda: self.stuf.__setitem__('max', 3))
        self.stuf.clear()
        self.stuf['test1'] = 'test1again'
        self.stuf['test3'] = 5

    def test_pop(self):
        self.assertRaises(AttributeError, lambda: self.stuf.test3.pop('e'))
        self.assertRaises(AttributeError, lambda: self.stuf.pop('test1'))

    def test_popitem(self):
        self.assertRaises(AttributeError, lambda: self.stuf.test3.popitem())
        self.assertRaises(AttributeError, lambda: self.stuf.popitem())

    def test_setdefault(self):
        self.assertEqual(self.stuf.test3.setdefault('e', 8), 1)
        self.assertRaises(KeyError, lambda: self.stuf.test3.setdefault('r', 8))
        self.assertEqual(self.stuf.setdefault('test1', 8), 'test1')
        self.assertRaises(KeyError, lambda: self.stuf.setdefault('pow', 8))


class TestFrozenStuf(Base, unittest.TestCase):

    @property
    def _impone(self):
        from stuf import frozenstuf
        return frozenstuf

    def test__setattr__(self):
        self.assertRaises(AttributeError, setattr(self.stuf, 'max', 3))
        self.assertRaises(
            AttributeError, setattr(self.stuf, 'test1', 'test1again')
        )
        self.assertRaises(
            AttributeError, setattr(self.stuf.test3, 'e', 5)
        )

    def test__setitem__(self):
        self.assertRaises(
            AttributeError, lambda: self.stuf.__setitem__('max', 3)
        )
        self.assertRaises(
            AttributeError,
            lambda: self.stuf.__setitem__('test2', 'test2again'),
        )
        self.assertRaises(
            AttributeError, lambda: self.stuf.test3.__setitem__('e', 5)
        )

    def test__delattr__(self):
        self.assertRaises(TypeError, lambda: delattr(self.stuf.test1))
        self.assertRaises(TypeError, lambda: delattr(self.stuf.test3.e))

    def test__delitem__(self):
        self.assertRaises(
            AttributeError, lambda: self.stuf.__delitem__('test1'),
        )
        self.assertRaises(
            AttributeError, lambda: self.stuf.test3.__delitem__('test1'),
        )

    def test_clear(self):
        self.assertRaises(AttributeError, lambda: self.stuf.test3.clear())
        self.assertRaises(AttributeError, lambda: self.stuf.clear())

    def test_pop(self):
        self.assertRaises(AttributeError, lambda: self.stuf.test3.pop('e'))
        self.assertRaises(AttributeError, lambda: self.stuf.pop('test1'))

    def test_popitem(self):
        self.assertRaises(AttributeError, lambda: self.stuf.test3.popitem())
        self.assertRaises(AttributeError, lambda: self.stuf.popitem())

    def test_setdefault(self):
        self.assertRaises(
            AttributeError, lambda: self.stuf.test3.setdefault('e', 8)
        )
        self.assertRaises(
            AttributeError, lambda: self.stuf.test3.setdefault('r', 8)
        )
        self.assertRaises(
            AttributeError, lambda: self.stuf.setdefault('test1', 8)
        )
        self.assertRaises(
            AttributeError, lambda: self.stuf.setdefault('pow', 8)
        )

    def test_update(self):
        tstuff = self._makeone
        self.assertRaises(
            AttributeError, lambda: self.stuf.test3.update(tstuff),
        )
        self.assertRaises(AttributeError, lambda: self.stuf.update(tstuff))


class TestOrderedStuf(Base, unittest.TestCase):

    @property
    def _impone(self):
        from stuf import orderedstuf
        return orderedstuf

    def test_reversed(self):
        slist = list(reversed(self.stuf))
        self.assertIn('test1', slist)
        self.assertIn('test2', slist)
        self.assertIn('test3', slist)


if __name__ == '__main__':
    unittest.main()
