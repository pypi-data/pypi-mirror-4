#!/usr/bin/env python

""" Test that auto-closing queue shuts down only when expected. """

import sys
import threading
import time


# When True, shows the program terminating abruptly.
# When False, shows improvement with autoclosing queue.
USE_STANDARD_QUEUE = False

if USE_STANDARD_QUEUE:
    from Queue import Queue
else:
    from autoclosingqueue import Queue

def main():
    queue = Queue()

    def consume(queue):
        while True:
            item = queue.get(timeout=1)
            print item
            time.sleep(1) # Don't process too quickly.
            if item:
                queue.task_done()

    consumer_thread = threading.Thread(
        name="Consumer Thread",
        target=consume,
        args=(queue,))
    consumer_thread.daemon = True
    consumer_thread.start()

    queue.put("1 of 4: This test needs manual inspection.")
    queue.put("2 of 4: It only passes if:")
    queue.put("3 of 4:    * All four messages are displayed.")
    queue.put("4 of 4:    * The program terminates.")

    # Finish main thread abruptly, without waiting for the consumer.
    # Application should still hang around to complete the task.

# Note: main() has to be last thing called in the process.

if __name__ == "__main__":
    main()
