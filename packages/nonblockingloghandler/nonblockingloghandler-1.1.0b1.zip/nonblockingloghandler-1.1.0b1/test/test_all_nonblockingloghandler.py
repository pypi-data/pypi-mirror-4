#!/usr/bin/env python

""" Run all available unit-tests.

    Some tests, outside the unittest framework, require manual inspection of
    the results.

    Designed to fit into the setup tools test framework, where possible.
    However, the tests requiring manual inspection are *not* run from setup
    tools.

"""

import unittest

from . import test_autoclosing_queue 
from . import test_autoclosing_queue_autocloses
from . import test_nonblockingloghandler_units
from . import test_nonblockingloghandler_stresstest
from . import test_nonblockingloghandler_termination_tests

def additional_tests():
    """
        Run all the unittest-compliant unit tests.
    
        Note: function name is specified by setuptools.
    """
    all_tests = unittest.TestSuite()
    for module_to_test in [
        test_autoclosing_queue,
        test_nonblockingloghandler_units,
        test_nonblockingloghandler_termination_tests
        ]:

        all_tests.addTests(
            unittest.defaultTestLoader.loadTestsFromModule(module_to_test))

    return all_tests

def run_all():
    """
        Run all the tests, including th eones requiring manual inspection.
    """
    
    # Run the unittest-compliant tests (also run on demand by setuptools)
    unittest.TextTestRunner(verbosity=10).run(additional_tests())
    
    # Run the non-unittest-compliant tests that require manual inspection.
    test_nonblockingloghandler_stresstest.stress_test() 
    test_autoclosing_queue_autocloses.main() # Must be last
