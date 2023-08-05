# Tests for subclasses of Immutable
#
# Written by Konrad Hinsen
#

import unittest

from immutable import Immutable, ImmutableTuple

class Test1(Immutable):

    def __init__(self, a, b):
        self.a = a
        self.b = b

class Test2(Test1):

    def __init__(self, a, b, c):
        Test1.__init__(self, a, b)
        self.c = c

class Test3(Immutable):

    def __init__(self, iterable):
        self.values = ImmutableTuple(iterable)

    def __getitem__(self, item):
        return self.values[item]

class Test4(Test1):

    pass

class ClassTests(unittest.TestCase):

    def test_normal_use(self):
        x = Test1(2, 3)
        self.assertEqual(x.a, 2)
        self.assertEqual(x.b, 3)
        self.assertTrue(isinstance(x, Immutable))
        x = Test4(2, 3)
        self.assertEqual(x.a, 2)
        self.assertEqual(x.b, 3)
        self.assertTrue(isinstance(x, Immutable))
        x = Test2(2, 3, 4)
        self.assertEqual(x.a, 2)
        self.assertEqual(x.b, 3)
        self.assertEqual(x.c, 4)
        self.assertTrue(isinstance(x, Immutable))
        x = Test1(Test1(2, 3), Test2(2, 3, 4))
        self.assertEqual(x.a, Test1(2, 3))
        self.assertEqual(x.b, Test2(2, 3, 4))
        x = Test3(range(10))
        for i in range(10):
            self.assertEqual(x[i], i)

    def test_hash(self):
        s = set([Test1(2, 3), Test2(2, 3, 4), Test1(2, 3)])
        self.assertEqual(len(s), 2)
        self.assertTrue(Test1(2, 3) in s)
        self.assertTrue(Test2(2, 3, 4) in s)

    def test_mutation_attempts(self):
        test1_instance = Test1(2, 3)
        test2_instance = Test2(2, 3, 4)
        test3_instance = Test3(range(10))
        test4_instance = Test4(2, 3)
        def seta(x): x.a = 42
        def setb(x): x.b = 42
        def setc(x): x.c = 42
        def setitem(x, i): x[i] = None
        for obj in [test1_instance, test2_instance,
                    test3_instance, test4_instance]:
            self.assertRaises(TypeError, seta, obj)
            self.assertRaises(TypeError, setb, obj)
            self.assertRaises(TypeError, setc, obj)
            self.assertRaises(TypeError, setitem, obj, 0)
    
    def test_mutable_attribute_values(self):
        def use_lists(): return Test1([], [])
        def use_tuples(): return Test1((), ())
        def use_dicts(): return Test2({}, {}, {})
        self.assertRaises(TypeError, use_lists)
        self.assertRaises(TypeError, use_tuples)
        self.assertRaises(TypeError, use_dicts)

    def test_mutable_subclasses(self):
        def subclass1():
            class Mutable1(Test1):
                def __setattr__(self, attr, value):
                    self.__dict__[attr] = value
        self.assertRaises(TypeError, subclass1)
        def subclass2():
            class Mutable3(Test3):
                def __setitem__(self, item, value):
                    self.values[item] = value
        self.assertRaises(TypeError, subclass2)
        def subclass3():
            class Mutable1(Test1):
                def __delattr__(self, attr):
                    del self.__dict__[attr]
        self.assertRaises(TypeError, subclass3)
        def subclass4():
            class Mutable3(Test3):
                def __delitem__(self, item):
                    del self.values[item]
        self.assertRaises(TypeError, subclass4)

def suite():
    loader = unittest.TestLoader()
    s = unittest.TestSuite()
    s.addTest(loader.loadTestsFromTestCase(ClassTests))
    return s

if __name__ == '__main__':
    unittest.main()
