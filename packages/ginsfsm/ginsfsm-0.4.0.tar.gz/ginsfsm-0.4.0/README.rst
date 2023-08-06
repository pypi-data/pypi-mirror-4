GinsFSM
=======

Do you can draw your development?

Do you can view the behaviour of your application in real time?

This framework can!.

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

Support and Documentation
-------------------------

See the <http://ginsfsm.org/> to view documentation.

Code available in <https://bitbucket.org/artgins/ginsfsm>

License
-------

Copyright (c) 2012, Ginés Martínez Sánchez.

GinsFSM is released under terms of The MIT
License <http://www.opensource.org/licenses/mit-license>
