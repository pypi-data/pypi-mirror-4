#
# Run with py.test
#

import pytest
import string
import gc
import time
import threading
try:
    import queue
except ImportError:
    import Queue as queue

from asyncthreads.reactor import Reactor


class TestReactor(object):

    @classmethod
    def setup_class(cls):
        gc.set_debug(
            gc.DEBUG_UNCOLLECTABLE|gc.DEBUG_INSTANCES|gc.DEBUG_OBJECTS)

        cls.rktr = Reactor(0)
        cls.called = False
        cls.cb_event = threading.Event()
        cls.cb_rsp = None
        cls.new_cb_called = False
        cls.defer_called = False


    def _func1(self):
        TestReactor.called = True
        return 'abc'

    def _func2(self, arg1, arg2):
        TestReactor.called = True
        return '-'.join([arg1, arg2])

    def _callback(self, result):
        TestReactor.cb_rsp = result.get_result()
        TestReactor.cb_event.set()

    def _new_cb(self, result):
        TestReactor.new_cb_called = True

    def _func_error(self):
        TestReactor.called = True
        raise Exception('some big problem')

    def _callback_error(self, result):
        TestReactor.cb_event.set()
        raise Exception('problem in callback')

    def _defer_func2(self, arg1, arg2):
        TestReactor.defer_called = True
        d = self.rktr.defer_to_thread(self._func2, (arg1, arg2))
        return d

    def _defer2_func2(self, arg1, arg2):
        TestReactor.defer_called = True
        d = self.rktr.defer_to_thread(self._func2, (arg1, arg2),
                                      self._new_cb)
        return d

    def reset_called(self):
        TestReactor.called = False
        TestReactor.cb_event.clear()
        TestReactor.cb_rsp = None
        TestReactor.defer_called = False
        TestReactor.new_cb_called = False

    def test_start(self):
        print 'Starting reactor'
        assert self.rktr is not None
        assert not self.rktr.is_alive()
        time.sleep(0)
        self.rktr.start()
        assert self.rktr.is_alive(), 'reactor should be alive'
        print 'started'


    def test_call(self):
        """Run in main thread"""
        print 'Calling function with no args in main thread'
        self.reset_called()
        result = self.rktr.call(self._func1)
        ret = result.get_result()
        assert self.called, 'called should be True'
        assert ret == 'abc', 'wrong result'

        print 'Calling function in main thread'
        self.reset_called()
        result = self.rktr.call(self._func2, ('hello', 'world'))
        ret = result.get_result()
        assert self.called, 'called should be True'
        assert ret == 'hello-world'

        print 'Calling function in main thread with callback'
        self.reset_called()
        result = self.rktr.call(self._func2, ('hello', 'world'),
                                self._callback)
        ret = result.get_result()
        assert self.called, 'called should be True'
        assert self.cb_event.wait(3), 'cb_event should be set'
        assert ret == 'hello-world'
        assert self.cb_rsp == 'hello-world'


    def test_call_in_thread(self):
        """Run in other thread"""
        print 'Calling function in other thread'
        self.reset_called()
        result = self.rktr.call_in_thread(self._func2, ('hello', 'world'))
        ret = result.get_result()
        assert self.called, 'called should be True'
        assert ret == 'hello-world'

        print 'Calling function in other thread with callback'
        self.reset_called()
        result = self.rktr.call_in_thread(self._func2, ('hello', 'world'),
                                          self._callback)
        ret = result.get_result()
        assert self.called, 'called should be True'
        assert self.cb_event.wait(3), 'cb_event should be set'
        assert ret == 'hello-world'
        assert self.cb_rsp == 'hello-world'


    def test_call_scheduled(self):
        """Run scheduled in main thread"""
        print 'Calling function in main thread in 3 seconds'
        self.reset_called()
        result = self.rktr.call_later(3, self._func2, ('hello', 'world'))

        assert not result.has_result(), 'should not have result yet'
        time.sleep(4)
        assert result.has_result(), 'should have result by now'

        ret = result.get_result()
        assert self.called, 'called should be True'
        assert ret == 'hello-world'

        print 'Calling function in main thread with callback in 3 seconds'
        self.reset_called()
        result = self.rktr.call_later(3, self._func2, ('hello', 'world'),
                                      self._callback)

        assert not result.has_result(), 'should not have result yet'
        time.sleep(4)
        assert result.has_result(), 'should have result by now'

        ret = result.get_result()
        assert self.called, 'called should be True'
        assert self.cb_event.wait(3), 'cb_event should be set'
        assert ret == 'hello-world'
        assert self.cb_rsp == 'hello-world'


    def test_call_in_thread_scheduled(self):
        """Run in other thread"""
        print 'Calling function in other thread in 3 seconds'
        self.reset_called()
        result = self.rktr.call_in_thread_later(3, self._func2,
                                                ('hello', 'world'))

        assert not result.has_result(), 'should not have result yet'
        time.sleep(4)
        assert result.has_result(), 'should have result by now'

        ret = result.get_result()
        assert self.called, 'called should be True'
        assert ret == 'hello-world'

        print 'Calling function in other thread with callback in 3 seconds'
        self.reset_called()
        result = self.rktr.call_in_thread_later(
            3, self._func2, ('hello', 'world'), self._callback)

        assert not result.has_result(), 'should not have result yet'
        time.sleep(4)
        assert result.has_result(), 'should have result by now'

        ret = result.get_result()
        assert self.called, 'called should be True'
        assert self.cb_event.wait(3), 'cb_event should be set'
        assert ret == 'hello-world'
        assert self.cb_rsp == 'hello-world'


    def test_cancel_scheduled(self):
        """Cancel scheduled call"""
        self.reset_called()
        print 'Calling function in 3 seconds'
        result = self.rktr.call_later(3, self._func2, ('hello', 'world'))
        assert not result.has_result(), 'should not have result yet'

        assert self.rktr.cancel_scheduled(result),\
               'failed to find scheduled task'
        time.sleep(4)
        rsp = result.get_result()
        assert result.is_canceled(), 'failed to mark result as canceled'

        assert rsp is None, 'result should be None'
        assert not self.called, 'called should be False'


    def test_exception_in_call(self):
        print 'Calling function in main thread that raises exception'
        self.reset_called()
        result = self.rktr.call(self._func_error)
        # Check for expected excption
        ret = None
        with pytest.raises(Exception) as ex:
            ret = result.get_result()
            assert str(ex) == 'some big problem'
        assert self.called, 'called should be True'
        assert ret is None, 'return should be None'
        assert len(result.get_traceback()) > 0, 'should be traceback info'

        print 'Calling function in other thread that raises exception'
        self.reset_called()
        result = self.rktr.call_in_thread(self._func_error)

        # Check for expected excption
        ret = None
        with pytest.raises(Exception) as ex:
            ret = result.get_result()
            assert str(ex) == 'some big problem'
        assert self.called, 'called should be True'
        assert ret is None, 'return should be None'
        assert len(result.get_traceback()) > 0, 'should be traceback info'


    def test_exception_in_callback(self):
        print 'Calling function in main thread that raises exception'
        self.reset_called()
        result = self.rktr.call(self._func1, (), self._callback_error)
        assert self.cb_event.wait(3), 'cb_event should be set'
        with pytest.raises(Exception) as ex:
            result.get_result()
            assert str(ex) == 'problem in callback'
        assert self.called, 'called should be True'
        assert len(result.get_traceback()) > 0, 'should be traceback info'


    def test_defer_call(self):
        print 'Calling func on reactor thread that defers processing to thread'
        self.reset_called()
        result = self.rktr.call(self._defer_func2, ('hello', 'world'))
        ret = result.get_result()
        assert self.called, 'called should be True'
        assert ret == 'hello-world'


    def test_defer_call_with_new_cb(self):
        print 'Calling func on reactor thread that defers processing to '\
              'thread and sets new callback'
        self.reset_called()
        result = self.rktr.call(self._defer2_func2, ('hello', 'world'))
        ret = result.get_result()
        assert self.called, 'called should be True'
        assert self.new_cb_called,\
               'new callback not called by deferred thread'
        assert ret == 'hello-world'


    def test_result_queue(self):
        print 'Calling 3 functions in pooled thread, with delay of 1, 2, and '\
              '3 seconds for each thread, and waiting for all results on '\
              'same result queue.'
        self.reset_called()
        rq = queue.Queue()
        self.rktr.call_in_thread_later(1, self._func2, ('delay', 'one'), None,
                                       rq)
        self.rktr.call_in_thread_later(2, self._func2, ('delay', 'two'), None,
                                       rq)
        self.rktr.call_in_thread_later(3, self._func2, ('delay', 'three'),
                                       None, rq)
        count = 0
        while count < 3:
            r = rq.get(True, 5)
            count += 1
            ret = r.get_result()
            print 'got result:', ret
            if count == 1:
                assert ret == 'delay-one'
            elif count == 2:
                assert ret == 'delay-two'
            else:
                assert ret == 'delay-three'


    def test_shutdown(self):
        print 'Shutting down reactor'
        self.rktr.shutdown()
        assert not self.rktr.is_alive(), 'reactor should not be alive'


    def test_memory_leaks(self):
        """Check for memory leaks"""
        # Test for any objects that cannot be freed.
        assert len(gc.garbage) == 0, 'uncollected garbage: '+str(gc.garbage)



