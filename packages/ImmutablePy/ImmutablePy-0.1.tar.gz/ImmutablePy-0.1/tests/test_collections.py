# Tests for subclasses of Immutable
#
# Written by Konrad Hinsen
#

import unittest

from immutable import Immutable, ImmutableTuple, ImmutableDict, ImmutableSet

class T(ImmutableTuple):

    # This is called for slicing in Python 2
    def __getslice__(self, start, end):
        return T(ImmutableTuple.__getslice__(self, start, end))

    # This is called for slicing in Python 3, with a slice argument
    def __getitem__(self, item):
        if isinstance(item, slice):
            return T(ImmutableTuple.__getitem__(self, item))
        else:
            return ImmutableTuple.__getitem__(self, item)

class CollectionTests(unittest.TestCase):

    def test_tuples(self):
        t1 = ImmutableTuple((1, 2, 3))
        t2 = ImmutableTuple((4, 5))
        self.assertTrue(isinstance(t1, Immutable))
        self.assertTrue(isinstance(t2, Immutable))
        self.assertTrue(isinstance(t1+t2, Immutable))
        self.assertTrue(isinstance(t1[1:], Immutable))
        self.assertTrue(isinstance(t2.append(42), Immutable))

    def test_sets(self):
        s1 = ImmutableSet((1, 2, 3, 2, 1))
        s2 = ImmutableSet((4, 5, 1))
        self.assertEqual(len(s1), 3)
        self.assertEqual(len(s2), 3)
        self.assertEqual(len(s1.union(s2)), 5)
        self.assertEqual(len(s1.intersection(s2)), 1)
        self.assertEqual(len(s1.symmetric_difference(s2)), 4)
        self.assertEqual(len(s1.add(4)), 4)
        self.assertEqual(len(s1.add(3)), 3)
        self.assertTrue(isinstance(s1, Immutable))
        self.assertTrue(isinstance(s2, Immutable))
        self.assertTrue(isinstance(s1.union(s2), Immutable))
        self.assertTrue(isinstance(s1.intersection(s2), Immutable))
        self.assertTrue(isinstance(s1.add(4), Immutable))
        self.assertEqual(s1.union(s2), s1 | s2)
        self.assertEqual(s1.intersection(s2), s1 & s2)
        self.assertEqual(s1.symmetric_difference(s2), s1 ^ s2)

    def test_dicts(self):
        d1 = ImmutableDict(a=1, b=2)
        d2 = ImmutableDict(c=3)
        self.assertTrue(isinstance(d1, Immutable))
        self.assertTrue(isinstance(d2, Immutable))
        self.assertTrue(isinstance(d1.update(d2), Immutable))
        self.assertEqual(len(d1), 2)
        self.assertEqual(len(d2), 1)
        self.assertEqual(len(d1.update(d2)), 3)

    def test_mutable_elements(self):
        self.assertRaises(TypeError, lambda: ImmutableTuple(([1], 2, 3)))
        self.assertRaises(TypeError, lambda: ImmutableSet(([1], 2, 3)))
        self.assertRaises(TypeError, lambda: ImmutableDict(l=[]))

    def test_subclassing(self):
        t = T(range(10))
        self.assertTrue(isinstance(t, Immutable))
        self.assertTrue(isinstance(t, ImmutableTuple))
        self.assertTrue(isinstance(t, T))
        s = t[2:]
        self.assertTrue(isinstance(s, Immutable))
        self.assertTrue(isinstance(s, ImmutableTuple))
        self.assertTrue(isinstance(s, T))

def suite():
    loader = unittest.TestLoader()
    s = unittest.TestSuite()
    s.addTest(loader.loadTestsFromTestCase(CollectionTests))
    return s

if __name__ == '__main__':
    unittest.main()

