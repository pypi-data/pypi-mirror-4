"""
Example of writing an XMLRPC server, using SimpleXMLRPCServer and replacing the
ThreadingMixIn with a version that uses the Reactor.

"""
import threading
try:
    from SimpleXMLRPCServer import (
        SimpleXMLRPCServer, SimpleXMLRPCRequestHandler)
except ImportError:
    from xmlrpc.server import SimpleXMLRPCServer, SimpleXMLRPCRequestHandler

from asyncthreads import reactor


# Restrict to a particular path.
class RequestHandler(SimpleXMLRPCRequestHandler):
    pass

# Create ReactorMixIn as a replacement for SocketServer.ThreadingMixIn
class ReactorMixIn:
    """Mix-in class to handle each request using reactor."""

    def process_request_thread(self, request, client_address):
        """Same as in BaseServer but as a thread.

        In addition, exception handling is done here.

        """
        try:
            self.finish_request(request, client_address)
            self.shutdown_request(request)
        except:
            self.handle_error(request, client_address)
            self.shutdown_request(request)

    def process_request(self, request, client_address):
        """Use reactor's thread pool to process the request."""
        self._reactor.call_in_thread(self.process_request_thread,
                                     (request, client_address))

# Create ThreadedRPCServer using ReactorMixIn instead of ThreadingMixin.
class ThreadedRPCServer(ReactorMixIn, SimpleXMLRPCServer):
    pass


class ExampleServer(object):

    def __init__(self, listen_addr='127.0.0.1', rpc_port=8080):
        self._shutdown_event = threading.Event()

        # Number of threads in pool.
        pooled_threads = 4
        # Create Reactor.
        self._reactor = reactor.Reactor(pooled_threads)

        # Create XML-RPC server
        self._server = ThreadedRPCServer(
            (listen_addr, rpc_port), RequestHandler)
        self._server._reactor = self._reactor

        # Register methods to expose for XMLRPC.
        self._server.register_function(self.foo)
        self._server.register_function(self.bar)
        self._server.register_function(self.baz)


    def start(self, blocking=True):
        self._reactor.start()

        # Start XMLRPC server
        self._rpc_thread = threading.Thread(target=self._run_xmlrpc_server)
        self._rpc_thread.start()

        if blocking:
            print('ctrl-c to exit')
            try:
                # Wake up every 5 seconds to check for KeyboardInterrupt.
                while not self._shutdown_event.wait(5):
                    pass
            except KeyboardInterrupt:
                pass
            self.shutdown()


    def shutdown(self):
        self._shutdown_event.set()
        self._server.shutdown()
        self._server.server_close()
        self._reactor.shutdown()
        self._rpc_thread.join()


    def _run_xmlrpc_server(self):
        try:
            self._server.serve_forever()
        except Exception as ex:
            print('XMLSERVER EXCEPTION: '+str(ex))
            self.shutdown()


    #==========================================================================
    # RPC API
    #
    def foo(self):
        print('called foo')
        return False

    def bar(self):
        print('called bar')
        return False

    def baz(self):
        print('called baz')
        return False


if __name__ == '__main__':
    s = ExampleServer()
    s.start()

