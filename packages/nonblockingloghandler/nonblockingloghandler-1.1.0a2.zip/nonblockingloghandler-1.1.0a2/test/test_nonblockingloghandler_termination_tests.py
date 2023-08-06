#!/usr/bin/env python

from os.path import dirname, join
import subprocess
import time
import unittest

class TestNonblockingLogHandlerTerminationTests(unittest.TestCase):
    
    def execute_and_check_terminates(self, command, period_to_wait = 10):
        external_program = subprocess.Popen(command)
        poll_period = 0.25 # seconds
        total_polls = int(period_to_wait / poll_period)
        for junk_i in range(total_polls):
            time.sleep(poll_period)
            if external_program.poll() is not None:
                self.assertEquals(external_program.returncode, 0)
                # Program terminated. Test passed.
                break
        else:
            # Program didn't terminate in time. Test failed.
            external_program.kill()
            self.fail("Test failed to self-terminate")

    def run_one_test(self, test_id):
        # Assumes python is on path, called 'python'.
        path = join(dirname(__file__),
                    'test_nonblockingloghandler_termination_subtest%d.py'
                        % test_id)
        self.execute_and_check_terminates("python %s" % path)

    def test_terminations(self):
        for test_id in xrange(1, 4):
            self.run_one_test(test_id)

if __name__ == "__main__":
    unittest.main()
