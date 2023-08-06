#!/usr/bin/env python

""" Straightforward tests of Autoclosing Queue.

    Does not test the real use-case, which requires the application to terminate."""

import unittest
import autoclosingqueue

class TestAutoClosingQueue(unittest.TestCase):

    def test_null_case(self):
        queue = autoclosingqueue.Queue()

    def test_simple_case(self):
        queue = autoclosingqueue.Queue()
        queue.put("Item")
        assert queue._undone_item_count == 1 # Peeking inside private, without mutex: Doubly naughty, but safe.
        assert queue.get() == "Item"
        assert queue._undone_item_count == 1 # Haven't marked as done yet.
        queue.task_done()
        assert queue._undone_item_count == 0

if __name__ == "__main__":
    unittest.main()
