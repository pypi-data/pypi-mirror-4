#!/usr/bin/env python

# Test what happens if the client isn't careful about cleaning up the log handlers. Does it shut-down correctly?

# Cannot be included with other tests in the same Python interpreter.
# Note: There are three variants to this test.
# Deliberately has no stdout. This test passes if it terminates.

import logging
import logging.handlers

import nonblockingloghandler

def termination_test_with_close():
    basic_logger = logging.handlers.MemoryHandler(1000) # Store to memory. Don't output.
    nh = nonblockingloghandler.NonblockingLogHandler(basic_logger)
    logging.getLogger("").addHandler(nh)
    logging.error("Logging message")
    nh.close() # In this test, we explicitly close the handler

import threading
thread = threading.Thread(target=termination_test_with_close)
thread.start()
