#!/usr/bin/env python

# Test that under extreme conditions, the logging doesn't use up too many system resources.
# This test FAILED in version 0.2 and 0.3.

import logging
import logging.handlers
import sys
import time
import unittest

import nonblockingloghandler

def stress_test():
    stdout_handler = logging.StreamHandler(sys.stdout)
    nh = nonblockingloghandler.NonblockingLogHandler(stdout_handler)
    logging.getLogger("").addHandler(nh)
    repetitions = 2000
    for i in xrange(repetitions + 1):
        #if i%100 == 0:
        #    print "CLIENT THREAD: Up to message # %s" % i
        logging.error("  Test in progress: %s of %s complete", i, repetitions)

    logging.error("TEST PASSED") # Failure is seen with an exception.
    time.sleep(15) # Give the threads a chance to catch up before the next test.
    print "Test completed."
if __name__ == "__main__":
    stress_test()
