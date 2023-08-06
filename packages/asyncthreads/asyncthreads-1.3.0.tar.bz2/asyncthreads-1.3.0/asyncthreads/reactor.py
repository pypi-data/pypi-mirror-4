"""
Reactor pattern to call queued functions in a separate thread.

Functions can be queued to be called by the reactor main thread, or by a thread
in the reactor's thread pool.  Functions can be be queued to be called
immediately (as soon as calling thread is available), or queued to be called at
a specified later time.

"""
__author__ = "Andrew Gillis"
__license__ = "http://www.opensource.org/licenses/mit-license.php"
__maintainer__ = "Andrew Gillis"
__email__ = "gillis.andrewj@gmail.com"

import threading
import traceback
import heapq
import time
from collections import Callable
try:
    import queue
except ImportError:
    import Queue as queue

import threadpool


class Result(object):

    """
    A Result object is returned by a Reactor's call_() methods.

    The Result object allows the caller to wait for and retrieve the result of
    a function called by the Reactor.  This not only includes any return from
    the called function, but any exception as well.

    A Result object is also used to identify a scheduled function to cancel,
    and it can be used to check if a scheduled call has been canceled.

    """

    slots = ('_call_done', '_rsp', '_exception', '_traceback_str', '_task_id',
             '_result_q')
    def __init__(self, result_q):
        self._call_done = threading.Event()
        self._rsp = None
        self._exception = None
        self._traceback_str = None

        # For canceling scheduled tasks.
        self._task_id = None

        # Optional queue to put this Result on when completed.
        self._result_q = result_q


    def get_result(self, timeout=None):
        if self._call_done.wait(timeout):
            if self._exception:
                raise self._exception

            return self._rsp
        return None


    def has_result(self):
        return self._call_done.is_set()


    def get_traceback(self):
        return self._traceback_str


    def is_canceled(self):
        return self._task_id is False


class _Deferred(object):
    # Internal object used to transition from execution in main thread to
    # execution in pool thread.
    #
    slots = ('action_tuple',)
    def __init__(self, func, args=None, callback=None):
        self.action_tuple = (func, args, callback)


class Reactor(threading.Thread):

    """
    The Reactor executes queued functions in a single thread.  Functions can be
    executed immediately, in the order they are enqueued, or they can be
    executed at some later time.  Functions may also be executed, immediately
    or later, in threads separate from the reactor's main thread.

    All functions executed by the reactor have an associated Result object.
    A Result object allows the caller to wait for and retrieve the result of a
    function called by the reactor.

    The reason to use a Reactor is to execute functions in a separate thread,
    asynchronously, from the thread of the caller.

    """

    # How long to wait for thread to shutdown.
    SHUTDOWN_FAILURE_TIMEOUT_SEC = 10


    def __init__(self, thread_pool_size=0, queue_size=None):
        """
        Initialize Reactor thread object and internal thread pool (if used).

        Arguments:
        pool_size     -- Number of threads to have in pool.  If this is set to
                         0 or None, then the reactor will not use a thread pool
                         and will start threads directly.
        queue_size    -- Maximum items allowed in task queue.  None means no
                         limit.  This is ignored if thread pool not used.

        """
        threading.Thread.__init__(self, None, None, None)
        self._call_queue = queue.Queue()
        self.idle_wake_sec = None
        if thread_pool_size:
            self._thread_pool = threadpool.ThreadPool(thread_pool_size,
                                                      queue_size)
        else:
            self._thread_pool = None

        self._task_heap = []


    def call(self, func, args=None, callback=None, result_q=None):
        """
        Enqueue a function for the reactor to run in its main thread.

        The caller can wait on the response using the returned Result object.
        Running a function in the reactor's main thread means that no other
        functions will be running in the reactor's main thread at the same
        time.  This can be used in place of other synchronization.

        Arguments:
        func     -- Function to execute.
        args     -- Argument tuple to pass to function.
        callback -- Optional callback that takes a Result as its argument.
        result_q -- Optional response queue to place complete Result on.

        Return:
        Result object.

        """
        assert(self.is_alive()), 'reactor is not started'
        assert(isinstance(func, Callable)), 'function is not callable'
        assert(callback is None or
               isinstance(callback, Callable)),'callback is not callable'
        assert(result_q is None or
               isinstance(result_q, queue.Queue)), 'result_q is not Queue'
        result = Result(result_q)
        self._call_queue.put((func, args, result, callback))
        return result


    def call_later(self, time_until_call, func, args=None, callback=None,
                   result_q=None):
        """
        Run a function in the reactor's main thread at a later time.

        The caller can wait on the response using the returned Result object.

        Arguments:
        time_until_call -- Seconds remaining until call.
        func            -- Function to execute.
        args            -- Argument tuple to pass to function.
        callback        -- Optional callback that takes a Result as its
                           argument.
        result_q        -- Optional response queue to place complete Result on.

        Return:
        Result object.

        """
        assert(self.is_alive()), 'reactor is not started'
        assert(isinstance(func, Callable)), 'function is not callable'
        assert(callback is None or
               isinstance(callback, Callable)), 'callback is not callable'
        if time_until_call:
            action_time = time.time() + time_until_call
        else:
            action_time = 0

        result = Result(result_q)
        d_data = (func, args, result, callback)
        self._call_queue.put((None, d_data, action_time, False))
        return result


    def call_in_thread(self, func, args=None, callback=None, result_q=None):
        """
        Run the given function in a separate thread.

        The caller can wait on the response using the returned Result object.
        A thread from the reactor's internal thread pool is used to avoid the
        overhead of creating a new thread.

        Arguments:
        func     -- Function to execute.
        args     -- Argument tuple to pass to function.
        callback -- Optional callback that takes a Result as its argument.
        result_q -- Optional response queue to place complete Result on.

        Return:
        Result object.

        """
        assert(self.is_alive()), 'reactor is not started'
        assert(isinstance(func, Callable)), 'function is not callable'
        assert(callback is None or
               isinstance(callback, Callable)), 'callback is not callable'
        result = Result(result_q)
        if self._thread_pool:
            self._thread_pool.queue_task(self._thread_wrapper,
                                         (func, args, result, callback))
        else:
            th = threading.Thread(target=self._thread_wrapper,
                                  args=(func, args, result, callback))
            th.daemon = True
            th.start()
        return result


    def call_in_thread_later(self, time_until_call, func, args=None,
                             callback=None, result_q=None):
        """
        Run the given function in a separate thread, at a later time.

        The caller can wait on the response using the returned Result object.
        A thread from the reactor's internal thread pool is used to avoid the
        overhead of creating a new thread.

        Arguments:
        time_until_call -- Seconds remaining until call.
        func            -- Function to execute.
        args            -- Argument tuple to pass to function.
        callback        -- Optional callback that takes a Result as its
                           argument.
        result_q        -- Optional response queue to place complete Result on.

        Return:
        Result object.

        """
        assert(self.is_alive()), 'reactor is not started'
        assert(isinstance(func, Callable)), 'function is not callable'
        assert(callback is None or
               isinstance(callback, Callable)), 'callback is not callable'
        if time_until_call:
            action_time = time.time() + time_until_call
        else:
            action_time = 0

        result = Result(result_q)
        d_data = (func, args, result, callback)
        self._call_queue.put((None, d_data, action_time, True))
        return result


    def cancel_scheduled(self, result):
        """
        Cancel a call scheduled to be called at a later time.

        Arguments:
        result -- Result object returned from call_later() or from
                  call_in_thread_later().

        Return:
        True if scheduled call was successfully canceled.  False if scheduled
        call was not found (already executed) or already canceled.

        """
        # The result's task_id cannot be checked in this method.  The request
        # must be placed on the reactor's call queue to ensure that a scheduled
        # task request is received by the reactor before this request to cancel
        # it is received.
        tmp_result = self.call(self._cancel_scheduled, result)
        # Wait for reactor to remove task, and return whether or not the task
        # was removed.
        return tmp_result.get_result()


    def shutdown(self):
        """
        Cause the reactor thread to exit gracefully.

        """
        if not self.is_alive():
            #print "thread is not started"
            return False

        self._call_queue.put(None)
        if self._thread_pool is not None:
            self._thread_pool.shutdown()

        # Wait for thread to exit.
        self.join(Reactor.SHUTDOWN_FAILURE_TIMEOUT_SEC)
        if self.is_alive():
            #print '===> timed out waiting to join:', self.getName()
            return False

        #print '===> thread exited:', self.getName()
        return True


    def qsize(self):
        """Return number of items in the message queue."""
        return self._call_queue.qsize()


    def empty(self):
        """Return True is no items in the message queue."""
        return self._call_queue.empty()


    def defer_to_thread(self, func, args=None, callback=None):
        """
        Defer execution from main thread to pooled thread, and use the caller's
        Result object to return the result of the additional execution.

        Arguments:
        func     -- Function to execute in pooled thread.
        args     -- Arguments to pass to func.
        callback -- Optional function to call with the Results of calling func.

        Returns:
        Special object recognized by Reactor to set up deferred call.

        """
        return _Deferred(func, args, callback)


    #==========================================================================
    # Private methods follow:
    #==========================================================================

    def _thread_wrapper(self, func, args, result, callback):
        try:
            if args is None:
                rsp = func()
            elif isinstance(args, (tuple, list, set)):
                rsp = func(*args)
            elif isinstance(args, dict):
                rsp = func(**args)
            else:
                rsp = func(args)
        except Exception as e:
            rsp = None
            result._exception = e
            result._traceback_str = traceback.format_exc()

        if isinstance(rsp, _Deferred):
            func, args, new_callback = rsp.action_tuple
            if new_callback is not None:
                callback = new_callback
            if self._thread_pool:
                self._thread_pool.queue_task(
                    self._thread_wrapper, (func, args, result, callback))
            else:
                th = threading.Thread(
                    target=self._thread_wrapper,
                    args=(func, args, result, callback))
                th.daemon = True
                th.start()
            return

        result._rsp = rsp
        result._call_done.set()
        if callback:
            try:
                callback(result)
            except Exception as e:
                rsp = None
                result._exception = e
                result._traceback_str = traceback.format_exc()
        if result._result_q:
            result_q = result._result_q
            result._result_q = None
            try:
                result_q.put(result)
            except queue.Full:
                pass


    def _process_scheduled_queue(self):
        """
        Process all scheduled tasks that are currently due.

        """
        task_heap = self._task_heap
        # Execute the first task without checking the time, because this method
        # is only called when a scheduled task is due.
        task_time, task_id, task_data, call_in_thread = heapq.heappop(
            task_heap)

        # If this task has been removed, then do nothing.
        if task_data is None:
            return

        def do_sched_task(func, args, result, callback):
            if call_in_thread:
                if self._thread_pool is not None:
                    # Call thread pool to execute scheduled function.
                    self._thread_pool.queue_task(
                        self._thread_wrapper, (func, args, result, callback))
                else:
                    # Create new thread to execute scheduled function.
                    th = threading.Thread(
                        target=self._thread_wrapper,
                        args=(func, args, result, callback))
                    th.daemon = True
                    th.start()
            else:
                #print '===> calling scheduled function'
                self._thread_wrapper(func, args, result, callback)


        do_sched_task(*task_data)
        if task_heap:
            now = time.time()
            next_time = task_heap[0][0]
            while task_heap and (not next_time or next_time <= now):
                task_time, task_id, task_data, call_in_thread = heapq.heappop(
                    task_heap)
                do_sched_task(*task_data)
                if task_heap:
                    next_time = task_heap[0][0]


    def _cancel_scheduled(self, result):
        """
        Mark a scheduled call, in scheduled task heap, as canceled.

        """
        task_id = result._task_id
        if task_id is None or task_id is False:
            # Task is not scheduled or is already canceled.
            return False
        task_heap = self._task_heap
        for idx, heap_item in enumerate(task_heap):
            task_time, heap_task_id, task_data, call_in_thread = heap_item
            if heap_task_id == task_id:
                func, args, result, callback = task_data
                result._rsp = None
                result._task_id = False
                result._call_done.set()
                # Need to keep task_id to preserve heap invariant.
                task_heap[idx] = (task_time, heap_task_id, None, None)
                return True
        return False


    def run(self):
        """
        Function run in thread, started by the start() method.

        """
        call_queue = self._call_queue
        task_heap = self._task_heap
        next_task_id = 0
        while True:
            sleep_time = None
            # If there are items on the scheduled task heap, then sleep until
            # next scheduled task is due.
            if task_heap:
                now = time.time()
                # Look at timer at top of heap.
                action_time = task_heap[0][0]
                if not action_time or action_time <= now:
                    sleep_time = 0
                else:
                    sleep_time = action_time - now

            try:
                #print '===> sleeping for %s seconds, or until next call put on queue' % (sleep_time,)
                # Get the next function from the call queue.
                action_tuple = call_queue.get(True, sleep_time)
                if action_tuple is None:
                    break
                func, args, result, callback = action_tuple

                # If this is a new scheduled task.
                if func is None:
                    time_to_call = result
                    call_in_thread = callback # callback is really thread flag
                    f,a,r,c = args
                    r._task_id = next_task_id
                    heapq.heappush(task_heap,
                                   (time_to_call, next_task_id, args,
                                    call_in_thread))
                    next_task_id += 1
                else:
                    self._thread_wrapper(func, args, result, callback)

            except queue.Empty:
                # Woke up because it is time do next scheduled task.
                #print '===> woke up to do next scheduled task'
                self._process_scheduled_queue()
                continue

            except Exception:
                print('ERROR: '+str(traceback.format_exc()))

        return True

