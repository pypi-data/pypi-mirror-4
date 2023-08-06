===================================================
Asynchronous Threads Utility -- asyncthreads
===================================================

The asyncthreads module provides common threading design patterns and utilities
needed for asynchronous and multithreaded programming.  This includes a thread
pool and a reactor, which together combine to create a highly reliable
concurrent event processing system.

Project Links
=============

 - Downloads: http://pypi.python.org/pypi/asyncthreads
 - Documentation: https://bitbucket.org/agillis/asyncthreads/wiki/Home
 - Project page: https://bitbucket.org/agillis/asyncthreads
 - License: http://www.opensource.org/licenses/mit-license.php

Installation
============

The asyncthreads package is installed from source using distutils in the usual way.  Download the `source distribution <http://pypi.python.org/pypi/asyncthreads>`_ first.  Un-tar the source tarball and run the following to install the package site-wide:

``python setup.py install``

Usage
=====

Using the ThreadPool and Reactor is as simple as creating an instance and submitting work::

 r = Reactor()
 r.start()
 r.call(handle_event, (transport, event_id))
 r.call_later(300, five_min_sync_check, (param1, param2))
 r.call_in_thread(background_task)
 r.call_in_thread_later(600, ten_min_async_check, (param1, param2))
 r.shutdown()

See the `documentation <https://bitbucket.org/agillis/asyncthreads/wiki/Home>`_ for details.

For example usage, look in the ``examples`` and ``test`` directories in `src <https://bitbucket.org/agillis/asyncthreads/src>`_.

Requirements
============

 - Python 2.7 or greater

Development Tools
=================

Development tools are only required for doing development work and running
tests.

 - mercurial
 - py.test
 - pychecker

Bugs and Issues
===============

http://bitbucket.org/agillis/asyncthreads/issues/
