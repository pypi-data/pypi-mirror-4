#!/usr/bin/env python

"""
    A drop-in replacement for Queue.queue, which protects the consumer's thread
    from being killed before the queue is empty.

    When to use it:
        When you are implementing pool of workers, AND:
          (a) the client does not promise to signal to the consumer thread that
              it is finished, and may shut-down, AND
          (b) the client does not promise to remain alive until the consumer
              thread is complete
          (c) you do not have a maximum queue size.

        Under these circumstances, you will find that:
            If the consumer threads are daemons, they may get shut down before
            processing is finished.
            If the consumer threads are not daemons, they may keep the
            application alive indefinitely, waiting for items that will
            never arrive.

    How to use it:
        * Make the consumer threads daemons (see threading.daemon).
        * Use this queue for communication instead of queue.Queue.
        * Important: Ensure that the consumer threads call task_done() when
          complete. 

    How it works:
        This object delegates the hard work to Queue.queue, but it also has its
        own thread. This thread is always alive when there is an item in the
        queue to be processed, and shuts down when there isn't. At most, one
        such thread is alive.

        The thread has no work to do; its role is just to prevent the Python
        run-time from shutting down the application, which it will do when
        there are only daemon threads remaining.

    Known Limitations:
        * task_done() must be called by consumer after processing each item, or
          application will never terminate.
        * PriorityQueues and LifoQueues are not supported, but could be.
        * maxsize is not supported, but could be with more complicated tracking
          of items.

"""
from Queue import Queue as base_queue
import threading

from nonblockingloghandlerversion import __version__ # Support PEP 396

class Queue(base_queue):
    """ Autoclosing Queue, that will not permit the application to gracefully
       shut-down until all tasks are done. """

    def __init__(self):
        base_queue.__init__(self, maxsize=0)
        self._undone_item_count_mutex = threading.Lock()

        # Count the number of items that have not yet been marked as done.
        # Always greater than or equal to the number of items in the queue.
        # Do not access without grabbing the above mutex
        self._undone_item_count = 0

        # A signalling mechanism to inform the protector thread it may shut
        # down.
        self.protector_thread_shutdown = threading.Semaphore(0)

    def put(self, item, block=True, timeout=None):
        # Note: block and timeout parameters are irrelevant, because maxsize is
        # guaranteed zero.
        # This simplifies the item counting.

        # Increment the outstanding items count, and start the protected thread
        # if required.
        with self._undone_item_count_mutex:
            self._undone_item_count += 1
            if self._undone_item_count == 1:
                # Just added first item; fire up the protector thread.
                threading.Thread(
                    name="NonblockingLogHandler.protector",
                    target=Queue._protect,
                    args=(self,)).start()

        base_queue.put(self, item, block, timeout)

    def task_done(self):
        base_queue.task_done(self)

        with self._undone_item_count_mutex:
            self._undone_item_count -= 1
            all_done = self._undone_item_count == 0
        if all_done:
            # No remaining items. Signal the protector thread it may shut-down.
            # (i.e. that the count should be decremented.)
            self.protector_thread_shutdown.release() 

    @staticmethod
    def _protect(autoclosingqueue):
        """ Method invoked by protector thread. """
        
        # Block waiting for task_done to be called.
        autoclosingqueue.protector_thread_shutdown.acquire() 
