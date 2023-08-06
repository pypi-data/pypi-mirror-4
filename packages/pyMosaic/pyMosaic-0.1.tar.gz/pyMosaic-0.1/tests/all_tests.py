# -*- coding: utf-8 -*-

# Run the complete test suite
#
# Written by Konrad Hinsen.
#

import unittest

import mutable_model_tests
import immutable_model_tests
import equivalence_tests
import hdf5_tests
import xml_tests

def suite():
    test_suite = unittest.TestSuite()
    test_suite.addTests(mutable_model_tests.suite())
    test_suite.addTests(immutable_model_tests.suite())
    test_suite.addTests(equivalence_tests.suite())
    test_suite.addTests(hdf5_tests.suite())
    test_suite.addTests(xml_tests.suite())
    return test_suite

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())

