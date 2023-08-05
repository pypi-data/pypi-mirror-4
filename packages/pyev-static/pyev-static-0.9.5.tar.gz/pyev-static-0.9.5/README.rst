==============================
pyev - Python libev interface.
==============================

CI status: |cistatus|

libev is an event loop: you register interest in certain events (such as a file
descriptor being readable or a timeout occurring), and it will manage these
event sources and provide your program with events.
To do this, it must take more or less complete control over your process (or
thread) by executing the event loop handler, and will then communicate events
via a callback mechanism.
You register interest in certain events by registering so-called event watchers,
which you initialise with the details of the event, and then hand over to libev
by starting the watcher.

libev supports ``select``, ``poll``, the Linux-specific ``epoll``, the
BSD-specific ``kqueue`` and the Solaris-specific ``event port`` mechanisms for
file descriptor events (``Io``), the Linux ``inotify`` interface (for
``Stat``), Linux ``eventfd``/``signalfd`` (for faster and cleaner
inter-thread wakeup (``Async``)/signal handling (``Signal``)),
relative timers (``Timer``), absolute timers (``Periodic``),
timers with customised rescheduling (``Scheduler``), synchronous signals
(``Signal``), process status change events (``Child``), and event
watchers dealing with the event loop mechanism itself (``Idle``,
``Embed``, ``Prepare`` and ``Check`` watchers) as well
as file watchers (``Stat``) and even limited support for fork events
(``Fork``).

It also is quite `fast <http://libev.schmorp.de/bench.html>`_.

libev is written and maintained by Marc Lehmann.

.. seealso::
    `libev's homepage <http://software.schmorp.de/pkg/libev>`_.


Useful links:

- `Latest release <http://pypi.python.org/pypi/pyev/>`_
- `Documentation <http://packages.python.org/pyev/>`_
- `Bug reports and feature requests
  <http://code.google.com/p/pyev/issues/list>`_


`pyev's source code <http://pyev.googlecode.com/>`_ is currently hosted by
`Google code <http://code.google.com/>`_ and kept in a
`Subversion <http://subversion.apache.org/>`_ repository.

- `Subversion instructions <http://code.google.com/p/pyev/source/checkout>`_
- `Subversion browser <http://code.google.com/p/pyev/source/browse/>`_

.. |cistatus| image:: https://secure.travis-ci.org/blackwithwhite666/pyev.png?branch=master
