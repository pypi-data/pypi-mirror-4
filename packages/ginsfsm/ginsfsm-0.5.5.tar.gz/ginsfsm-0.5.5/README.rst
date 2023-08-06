GinsFSM
=======

Can you draw your development?

Can you view the behaviour of your application in real time?

With this framework you can!.

GinsFSM is a python library to develop systems based in finite-state machines
(http://en.wikipedia.org/wiki/Finite-state_machine).
This model is really useful when writing networking and communication
applications.

The idea is very simple:

    * All objects, called `gobj`, are instances of a derived
      `ginsfsm.gobj.GObj` class.
    * The `GObj` has an inside `simple-machine`
      that defines its behavior.
    * The communication between `gobj`'s happens via `event`'s.

Thus, the nature of this system is fully asynchronous and event-driven.

The interface is simple and common to all objects; you just have to change the
name of the event and the data they carry.

It includes a full asynchronous http server, wsgi server
and winsocket server/client compatible with
`sockjs <https://github.com/sockjs/sockjs-client>`_.

You can run multiple wsgi applications.

Ginsfsm comes with a variety of scaffolds
that you can use to generate a project.

Like `Pyramid <http://www.pylonsproject.org/>`_ framework pcreate/pserve commands,
Ginsfsm provides the gcreate/gserve commands,
to create and run ginsfsm projects.

With gcreate command you can create a ginsfsm project.
For example, with multi_pyramid_wsgi scaffold,
you will create a multiple wsgi application project,
one of wsgi application being a `Pyramid <http://www.pylonsproject.org/>`_
wsgi application.

The GObj's objects are Pyramid "location-aware" resources.
Also, the gobj's are a hierarchical tree,
also therefore the use of traversal dispatching are all natural.

Support and Documentation
-------------------------

See the <http://ginsfsm.org/> to view documentation.

Code available in <https://bitbucket.org/artgins/ginsfsm>

License
-------

Copyright (c) 2012, Ginés Martínez Sánchez.

GinsFSM is released under terms of The MIT
License <http://www.opensource.org/licenses/mit-license>
