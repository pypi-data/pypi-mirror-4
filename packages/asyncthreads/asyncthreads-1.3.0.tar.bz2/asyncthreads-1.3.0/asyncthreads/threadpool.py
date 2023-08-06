"""
Resizable thread pool.

"""
__author__ = "Andrew Gillis"
__license__ = "http://www.opensource.org/licenses/mit-license.php"
__maintainer__ = "Andrew Gillis"
__email__ = "gillis.andrewj@gmail.com"

import threading
import time
from collections import Callable
try:
    import queue
except ImportError:
    import Queue as queue


class ThreadPool(object):

    """
    Resizable thread pool class.

    Maintain a pool of threads that execute tasks given to queue_task().  The
    number of worker whreads can be changed by calling resize_pool().

    """

    def __init__(self, pool_size, queue_size=None):
        """
        Initialize the thread pool and start the specified number of threads.

        Arguments:
        pool_size     -- Number of threads to have in pool.
        queue_size    -- Maximum items allowed in task queue.  None means no
                         limit.

        """
        assert(isinstance(pool_size, int)), 'pool_size is not an int'
        assert(queue_size is None or
               isinstance(queue_size, int)), 'queue_size is not an int'

        self.__shutting_down = False
        self.__threads = 0
        self.__task_queue = queue.Queue(queue_size)
        self.__resize_lock = threading.Condition(threading.Lock())

        self.resize_pool(pool_size)


    def queue_task(self, function, args=None, callback=None):
        """
        Insert a task function into the queue.

        """
        assert(isinstance(function, Callable)), 'function is not callable'
        assert(callback is None or
               isinstance(callback, Callable)), 'callback is not callable'

        if not self.__shutting_down:
            self.__task_queue.put((function, args, callback), False)


    def get_pool_size(self):
        """Return the number of threads in the pool."""
        return self.__threads


    def get_queue_size(self):
        """Return the number of items currently in task queue."""
        return self.__task_queue.qsize()


    def shutdown(self, wait_for_threads=True, drop_queued_tasks=False):
        """
        Shutdown the thread pool.

        Optionally wait for worker threads to exit, and optionally drop and
        queued tasks.

        Arguments:
        wait_for_threads  -- Wait for all threads to complete.
        drop_queued_tasks -- Discard any tasks that are on the task queue, but
                             have not yet been processed.

        Return:
        True if exited successfully, False if shutdown was already called.

        """
        if self.__shutting_down:
            return False

        self.__shutting_down = True

        # Discard remaining tasks on queue.
        while drop_queued_tasks:
            try:
                self.__task_queue.get(False)
                self.__task_queue.task_done()
            except queue.Empty:
                break

        self.resize_pool(0)
        if wait_for_threads:
            self.__task_queue.join()

        return True


    def resize_pool(self, new_size):
        """
        Resize the thread pool to have the specified number of threads.

        """
        if new_size < 0:
            raise ValueError('pool size must be >= 0')

        with self.__resize_lock:
            if new_size > self.__threads:
                # Growing pool.
                while self.__threads < new_size:
                    new_thread = _ThreadPoolThread(self.__task_queue)
                    new_thread.start()
                    self.__threads += 1
            else:
                # Shrinking pool.
                while self.__threads > new_size:
                    self.__task_queue.put(None)
                    self.__threads -= 1


class _ThreadPoolThread(threading.Thread):

    """
    Pooled thread class.

    """

    def __init__(self, task_queue):
        """
        Initialize pool thread.

        """
        threading.Thread.__init__(self)
        self.daemon = True
        self.__task_queue = task_queue


    def run(self):
        """
        Retrieve the next task and execute it, calling the callback if any.

        """
        task_queue = self.__task_queue
        while True:
            # Wait forever.
            task = task_queue.get()

            # Exit if told to quit.
            if task is None:
                task_queue.task_done()
                break

            # Execute task.
            func, args, callback = task
            try:
                if args is None:
                    ret = func()
                elif isinstance(args, (tuple, list, set)):
                    ret = func(*args)
                elif isinstance(args, dict):
                    ret = func(**args)
                else:
                    ret = func(args)

                if callback is not None:
                    callback(ret)
            except Exception as e:
                print('ThreadPool task raised exception: '+str(e))

            task_queue.task_done()

