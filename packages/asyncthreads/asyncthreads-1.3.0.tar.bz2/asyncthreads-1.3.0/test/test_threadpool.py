#
# Run with py.test
#

import gc
import time
from random import randrange

from asyncthreads.threadpool import ThreadPool

# Sample task 1: given a start and end value, shuffle integers,
# then sort them
def sort_task(first, last):
    print "SortTask starting for ", (first, last)
    numbers = range(first, last)
    for a in numbers:
        rnd = randrange(0, len(numbers) - 1)
        a, numbers[rnd] = numbers[rnd], a
    print "SortTask sorting for ", (first, last)
    numbers.sort()
    print "SortTask done for ", (first, last)
    return ("Sorter ", (first, last))

# Sample task 2: just sleep for a number of seconds.
def wait_task(data):
    print "WaitTask starting for ", data
    print "WaitTask sleeping for %d seconds" % data
    time.sleep(data)
    return "Waiter", data

# Both tasks use the same callback
def task_callback(data):
    print "Callback called for", data


class TestThreadPool(object):

    @classmethod
    def setup_class(cls):
        gc.set_debug(
            gc.DEBUG_UNCOLLECTABLE|gc.DEBUG_INSTANCES|gc.DEBUG_OBJECTS)

        cls.pool = ThreadPool(20, 256)


    def test_start(self):
        assert self.pool.get_pool_size() == 20
        self.pool.queue_task(wait_task, 15, task_callback)
        self.pool.queue_task(wait_task, 15, task_callback)
        self.pool.queue_task(wait_task, 15, task_callback)
        self.pool.queue_task(wait_task, 15, task_callback)
        self.pool.queue_task(wait_task, 15, task_callback)
        self.pool.queue_task(wait_task, 15, task_callback)
        self.pool.queue_task(wait_task, 15, task_callback)
        self.pool.queue_task(wait_task, 15, task_callback)
        self.pool.queue_task(wait_task, 15, task_callback)
        self.pool.queue_task(wait_task, 15, task_callback)
        self.pool.queue_task(wait_task, 15, task_callback)
        self.pool.queue_task(wait_task, 15, task_callback)
        self.pool.queue_task(wait_task, 15, task_callback)
        self.pool.queue_task(wait_task, 15, task_callback)
        self.pool.queue_task(wait_task, 15, task_callback)
        self.pool.queue_task(wait_task, 15, task_callback)
        self.pool.queue_task(wait_task, 15, task_callback)
        self.pool.queue_task(wait_task, 15, task_callback)
        self.pool.queue_task(wait_task, 15, task_callback)
        self.pool.queue_task(wait_task, 15, task_callback)
        self.pool.queue_task(wait_task, 15, task_callback)
        self.pool.queue_task(wait_task, 15, task_callback)
        self.pool.queue_task(wait_task, 15, task_callback)
        self.pool.queue_task(wait_task, 15, task_callback)
        self.pool.queue_task(wait_task, 15, task_callback)
        self.pool.queue_task(wait_task, 15, task_callback)
        self.pool.queue_task(wait_task, 15, task_callback)
        self.pool.queue_task(wait_task, 15, task_callback)
        self.pool.queue_task(wait_task, 15, task_callback)
        self.pool.queue_task(wait_task, 15, task_callback)
        self.pool.queue_task(wait_task, 15, task_callback)
        self.pool.queue_task(wait_task, 15, task_callback)
        self.pool.queue_task(wait_task, 15, task_callback)
        self.pool.queue_task(wait_task, 15, task_callback)
        self.pool.queue_task(wait_task, 15, task_callback)
        self.pool.queue_task(wait_task, 15, task_callback)
        self.pool.queue_task(wait_task, 15, task_callback)
        self.pool.queue_task(wait_task, 15, task_callback)
        self.pool.queue_task(wait_task, 15, task_callback)
        self.pool.queue_task(wait_task, 15, task_callback)
        self.pool.queue_task(wait_task, 15, task_callback)
        self.pool.queue_task(wait_task, 15, task_callback)
        self.pool.queue_task(wait_task, 15, task_callback)
        self.pool.queue_task(wait_task, 15, task_callback)
        self.pool.queue_task(wait_task, 15, task_callback)
        self.pool.queue_task(wait_task, 15, task_callback)
        # Insert tasks into the queue and let them run
        print 'start'
        self.pool.queue_task(sort_task, (1000, 100000), task_callback)
        self.pool.queue_task(wait_task, 5, task_callback)
        self.pool.queue_task(sort_task, (200, 200000), task_callback)
        self.pool.queue_task(wait_task, 2, task_callback)
        self.pool.queue_task(sort_task, (3, 30000), task_callback)
        self.pool.queue_task(wait_task, 7, task_callback)
        self.pool.queue_task(sort_task, (1000, 100000), task_callback)
        self.pool.queue_task(wait_task, 5, task_callback)
        self.pool.queue_task(sort_task, (200, 200000), task_callback)
        self.pool.queue_task(wait_task, 2, task_callback)
        self.pool.queue_task(sort_task, (3, 30000), task_callback)
        self.pool.queue_task(wait_task, 7, task_callback)
        self.pool.queue_task(sort_task, (201, 200001), task_callback)
        self.pool.queue_task(sort_task, (202, 200002), task_callback)
        self.pool.queue_task(sort_task, (203, 200003), task_callback)
        self.pool.queue_task(sort_task, (204, 200004), task_callback)
        self.pool.queue_task(sort_task, (205, 200005), task_callback)
        self.pool.queue_task(sort_task, (1000, 100000), task_callback)
        self.pool.queue_task(wait_task, 5, task_callback)
        self.pool.queue_task(sort_task, (200, 200000), task_callback)
        self.pool.queue_task(wait_task, 2, task_callback)
        self.pool.queue_task(sort_task, (3, 30000), task_callback)
        self.pool.queue_task(wait_task, 7, task_callback)
        self.pool.queue_task(sort_task, (1000, 100000), task_callback)
        self.pool.queue_task(wait_task, 5, task_callback)
        self.pool.queue_task(sort_task, (200, 200000), task_callback)
        self.pool.queue_task(wait_task, 2, task_callback)
        self.pool.queue_task(sort_task, (3, 30000), task_callback)
        self.pool.queue_task(wait_task, 7, task_callback)
        self.pool.queue_task(sort_task, (201, 200001), task_callback)
        self.pool.queue_task(sort_task, (202, 200002), task_callback)
        self.pool.queue_task(sort_task, (203, 200003), task_callback)
        self.pool.queue_task(sort_task, (204, 200004), task_callback)
        self.pool.queue_task(sort_task, (205, 200005), task_callback)

        for _ in range(3):
            print '---> queued items:', self.pool.get_queue_size()
            time.sleep(2)

        self.pool.resize_pool(80)
        assert self.pool.get_pool_size() == 80

        while self.pool.get_queue_size():
            print '---> queued items:', self.pool.get_queue_size()
            time.sleep(5)

        print 'finish'


    def test_shutdown(self):
        # When all tasks are finished, allow the threads to terminate
        print 'Shutting down thread pool'
        self.pool.shutdown(False, False)

        print '---> queued items:', self.pool.get_queue_size()
        while self.pool.get_queue_size():
            print '---> queued items:', self.pool.get_queue_size()
            time.sleep(5)


    def test_memory_leaks(self):
        """Check for memory leaks"""
        # Test for any objects that cannot be freed.
        assert len(gc.garbage) == 0, 'uncollected garbage: '+str(gc.garbage)

