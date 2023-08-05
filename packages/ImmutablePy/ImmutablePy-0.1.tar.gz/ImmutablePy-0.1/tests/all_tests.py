# Run the complete test suite
#
# Written by Konrad Hinsen.
#

import unittest

import test_classes
import test_collections

def suite():
    test_suite = unittest.TestSuite()
    test_suite.addTests(test_classes.suite())
    test_suite.addTests(test_collections.suite())
    return test_suite

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
