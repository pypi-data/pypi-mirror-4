#!/usr/bin/env python

import logging
import re
import time
import unittest

from nonblockingloghandler import NonblockingLogHandler

# Define a Logging Handler we can call and inspect.
class MockHandler(logging.Handler):
    def __init__(self):
        self.contents = []
        logging.Handler.__init__(self)

    def _store(self, name, sleep_period, *args, **kwargs):
        #print "MOCK CALLED %s()" % name
        time.sleep(sleep_period)
        self.contents.append("MockHandler::%s(%s, %s)" % (
            str(name),
            ((", ".join([str(arg) for arg in args])) if args else ""),
            kwargs if kwargs else ""
            )
        )
        return None

    @staticmethod
    def _dump(method_name="unspecified", sleep_period = 0):
        return lambda self, args = None: self._store(
            method_name, sleep_period, args)

MockHandler.close = MockHandler._dump("close")
MockHandler.format = MockHandler._dump("format")
MockHandler.createLock = MockHandler._dump("createLock")
MockHandler.acquire = MockHandler._dump("acquire")
MockHandler.release = MockHandler._dump("release")
MockHandler.setFormatter = MockHandler._dump("setFormatter")
MockHandler.flush = MockHandler._dump("flush")
MockHandler.emit = MockHandler._dump("emit", 0.01)
MockHandler.setLevel = MockHandler._dump("setLevel")

# Let the standard handler do its thing.
# MockHandler.handle = MockHandler._dump("handle") 

MockHandler.handleError = MockHandler._dump("handleError")

# Test utility
def assert_list_like_template(actual, desired):
    """Compare an actual list of strings with a desired list of regular
       expressions, and assert they are the same."""
    assert len(actual) == len(desired), ("Actual list length (%d)"
        "is different desired length (%d): %s"
        % (len(actual), len(desired), actual))
    for index, (actual_line, desired_line) in enumerate(zip(actual, desired)):
        assert re.match(desired_line, actual_line), (
            "Actual doesn't match desired (row = %s):\n"
            " Actual:  %s\n Desired: %s\nContext:\n  %s"
            % (index, actual_line, desired_line, "\n  ".join(actual))
            )

class TestNonblockingLogHandler(unittest.TestCase):

    def setUp(self):
        logging.basicConfig()
        for handler in logging.getLogger("").handlers[:]:
            logging.getLogger("").removeHandler(handler)
            handler.close()

    def test_mock_handler(self):
        # Make sure we have the test harness working before we start.
        mh = MockHandler()
        logging.getLogger("").addHandler(mh)
        logging.error("Error message")
        logging.getLogger("").removeHandler(mh)
        mh.close()
        time.sleep(2)
        
        assert_list_like_template(
            mh.contents, [
                r'MockHandler::createLock\(None, \)',
                r'MockHandler::acquire\(None, \)',
                r'MockHandler::emit\(<LogRecord: root, 40, [^,]*,'
                    r' \d+, "Error message"\>, \)',
                r'MockHandler::release\(None, \)',
                r'MockHandler::close\(None, \)'])

    def test_straightforward_usage(self):
        # Straight forward, single log message.
        mh = MockHandler()
        nh = NonblockingLogHandler(mh)
        logging.getLogger("").addHandler(nh)
        start_time = time.clock()
        logging.error("Error message")
        end_time = time.clock()
        assert end_time - start_time < 0.005, (
            "Spent too long: %s" % (end_time - start_time))
        time.sleep(0.02) # Give logging a chance before checking on it.
        logging.getLogger("").removeHandler(nh)
        nh.close()
        mh.close()
        assert_list_like_template(mh.contents, [
            r'MockHandler::createLock\(None, \)',
            r'MockHandler::acquire\(None, \)',
            r'MockHandler::emit\(<LogRecord: root, 40, [^,]*,'
                r' \d+, "Error message"\>, \)',
            r'MockHandler::release\(None, \)',
            r'MockHandler::close\(None, \)',
            ]
      )

    def test_basic_formatting(self):
        # Ensure substitutions are performed before the call is made.
        mh = MockHandler()
        nh = NonblockingLogHandler(mh)
        logging.getLogger("").addHandler(nh)
        logging.error("The wages of %s is %s", "sin", "death")
        time.sleep(0.05) # Give logging a chance before checking on it.
        logging.getLogger("").removeHandler(nh)
        nh.close()
        mh.close()        
        assert_list_like_template(mh.contents, ['MockHandler::createLock\(None, \)',
                                                'MockHandler::acquire\(None, \)',
                                                'MockHandler::emit\(<LogRecord: root, 40, [^,]*, \d+, "The wages of sin is death"\>, \)',
                                                'MockHandler::release\(None, \)',
                                                'MockHandler::close\(None, \)',
                                                ]
                                  )

    def test_multiple_calls(self):
        # Ensure that calls are queued.
        mh = MockHandler()
        nh = NonblockingLogHandler(mh)
        logging.getLogger("").addHandler(nh)
        start_time = time.clock()
        for i in range(30):
            logging.info("Info message") # Below threshold.
            logging.critical("Critical message")
            logging.warning("Warning message")
        end_time = time.clock()
        assert end_time - start_time < 60 * 0.005 # Delay of 0.25 is too much.
        time.sleep(10.030) # Give logging a chance before checking on it.
        logging.getLogger("").removeHandler(nh)
        nh.close()
        mh.close()        
        result_prefix = ['MockHandler::createLock\(None, \)']
        result_middle = 30 * [
            'MockHandler::acquire\(None, \)',
            'MockHandler::emit\(<LogRecord: root, 50, [^,]+, \d+, "Critical message">, \)',
            'MockHandler::release\(None, \)',
            'MockHandler::acquire\(None, \)',
            'MockHandler::emit\(<LogRecord: root, 30, [^,]+, \d+, "Warning message">, \)',
            'MockHandler::release\(None, \)',
        ]
        result_suffix =  ['MockHandler::close\(None, \)',]
        assert_list_like_template(mh.contents, result_prefix + result_middle + result_suffix)

    def test_multiple_calls_then_shutdown(self):
        # In Version 1.0.1, if the queue was still around when the handler was closed, the parent
        # would be closed before the queue had finished. This lead to very occasional
        # "I/O operation on closed file" issues.
        # This test inspects for that.
        
        mh = MockHandler()
        nh = NonblockingLogHandler(mh)
        logging.getLogger("").addHandler(nh)
        start_time = time.clock()
        for i in range(30):
            logging.info("Info message") # Below threshold.
            logging.critical("Critical message")
            logging.warning("Warning message")
        end_time = time.clock()
        assert end_time - start_time < 60 * 0.005 # Delay of 0.25 is too much.
        logging.getLogger("").removeHandler(nh)
        nh.close()
        # Note: Close BEFORE the processing is done.
        # We don't need to close MockHandler. It will be closed for us.
        time.sleep(10.030) # Give logging a chance before checking on it.
        result_prefix = ['MockHandler::createLock\(None, \)']
        result_middle = 30 * [
            'MockHandler::acquire\(None, \)',
            'MockHandler::emit\(<LogRecord: root, 50, [^,]+, \d+, "Critical message">, \)',
            'MockHandler::release\(None, \)',
            'MockHandler::acquire\(None, \)',
            'MockHandler::emit\(<LogRecord: root, 30, [^,]+, \d+, "Warning message">, \)',
            'MockHandler::release\(None, \)',
        ]
        expected_result = result_prefix + result_middle
        
        #for left, right in zip(expected_result, mh.contents):
        #    print '%40s %s %40s' % (left[:40], left == right, right[:40])
        assert_list_like_template(mh.contents, expected_result)
        mh.close()
        
    def test_set_formatter(self):
        # Ensure that setFormat gets through.
        mh = MockHandler()
        nh = NonblockingLogHandler(mh)
        logging.getLogger("").addHandler(nh)
        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        nh.setFormatter(formatter)
        logging.error("The wages of %s is %s", "sin", "death")
        time.sleep(0.05) # Give logging a chance before checking on it.
        logging.getLogger("").removeHandler(nh)
        nh.close()
        assert_list_like_template(mh.contents, ['MockHandler::createLock\(None, \)',
                                                'MockHandler::setFormatter\(<logging.Formatter[^,]*, \)',
                                                'MockHandler::acquire\(None, \)',
                                                'MockHandler::emit\(<LogRecord: root, 40, [^,]*, \d+, "The wages of sin is death"\>, \)',
                                                'MockHandler::release\(None, \)',
                                                ]
                                  )
        mh.close()

if __name__ == "__main__":
    unittest.main()
