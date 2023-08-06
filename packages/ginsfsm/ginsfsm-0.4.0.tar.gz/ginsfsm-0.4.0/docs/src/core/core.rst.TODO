==============
Inside GinsFSM
==============

Core
=====

Core GinsFSM is building with three main modules:

* :mod:`ginsfsm.gaplic`.
* :mod:`ginsfsm.gobj`.
* :mod:`ginsfsm.smachine`.

and three main classes:

* :class:`ginsfsm.gaplic.GAplic`.
* :class:`ginsfsm.gobj.GObj`.
* :class:`ginsfsm.smachine.SMachine`.

The :class:`ginsfsm.gaplic.GAplic` class is derived
from :class:`ginsfsm.gobj.GObj` class,
and the :class:`ginsfsm.gobj.GObj` class
is derived from :class:`ginsfsm.smachine.SMachine` class:

.. graphviz::

    digraph core_objects {
        graph [fontsize=30 labelloc="t" label="" splines=true overlap=false];
        size="7.0"
        node [shape="tab" penwidth=2 style=filled fillcolor="lightgray"];
        rankdir=TB;
        "GObj" [URL="http://xx\N"];
        "GAplic" [];
        "SMachine" [];
        "GObj" -> "GAplic";
        "SMachine" -> "GObj";
        }

The :mod:`ginsfsm.gaplic` module supplies support for:

* create :term:`gaplic` objects and running them as process or threads:
    * :ref:`running-as-thread`.
    * :ref:`running-as-main-process`.
    * :ref:`running-as-child-process`.

The :class:`ginsfsm.gaplic.GAplic` class supplies support for:

* create :term:`gobj` objects under his domain: :ref:`creating-gobj`.
* queues for exchange :term:`event`'s between :term:`gobj` objects.
* :ref:`infinite-loop` to run the process or thread.

The :mod:`ginsfsm.gobj` module supplies support for:

* :ref:`creating-gclass`.
* :ref:`creating-event`.

The :class:`ginsfsm.gobj.GObj` class supplies support for:

* :ref:`sending-events`:

    * sending events by direct delivery: :ref:`send-event`.
    * sending events by queues: :ref:`post-event`.
    * sending events to subscribers: :ref:`broadcast-event`.

* :ref:`receiving-events`:

    * directly from another :term:`gobj`'s who knows you.
    * subscribe to events from other :term:`gobj`'s: :ref:`subscription`.

Using gaplic
============

GAplic is the container of :term:`gobj`'s running under his domain:

.. graphviz::

    graph GAplic {
        size="6.0"
        graph [splines=true overlap=false];
        node [penwidth=2 style=filled fillcolor="lightgray"];
        subgraph cluster_thread_main {
            graph [style="filled" splines=true overlap=true];
            label="GAplic";
            "Principal gobj" -- "child1 gobj";
            "Principal gobj" -- "child2 gobj";
            "child2 gobj" -- "child2-1 gobj";
            "child2 gobj" -- "child2-2 gobj";
            "child1 gobj" -- "child1-1 gobj";
            "child2-1 gobj" -- "child2-1-1 gobj";
        }
    }

You can run a :term:`gaplic` as a simple process, a thread or
a child daemon process.

The :mod:`ginsfsm.gaplic` module build two classes with the same interface, to
run a :term:`gaplic` like a thread or process:

* :class:`ginsfsm.gaplic.GAplicProcessWorker`
* :class:`ginsfsm.gaplic.GAplicThreadWorker`

.. _running-as-main-process:

Running as main process
------------------------

For running as main process::

    if __name__ == "__main__":
        ga = GAplic()
        ga.create_gobj('test', GPrincipal, None)
        ga.mt_process()

.. _running-as-thread:

Running as thread
------------------

You can too run the :term:`gaplic` as a **thread** using
the :func:`ginsfsm.gaplic.start_gaplic_thread` function::

    if __name__ == "__main__":
        # run server gaplic as thread
        ga_srv = GAplic('ServerWorker')
        ga_srv.create_gobj('server', GServerPrincipal, None)
        srv_worker = start_gaplic_thread(ga_srv)

        # run client gaplic as main process
        ga_cli = GAplic('ClientWorker')
        ga_cli.create_gobj('client', GClientPrincipal, None)

        try:
            ga_cli.mt_process()
        except KeyboardInterrupt:
            srv_worker.shutdown()
            srv_worker.join()
            print('Program stopped')

.. _running-as-child-process:

Running as child process
------------------------

And you can too run the :term:`gaplic` as a **child daemon process** using
the :func:`ginsfsm.gaplic.start_gaplic_process` function::

    if __name__ == "__main__":
        # run server gaplic as child daemon process
        ga_srv = GAplic('ServerProcess')
        ga_srv.create_gobj('server', GServerPrincipal, None)
        srv_worker = start_gaplic_process(ga_srv)

        # run client gaplic as main process
        ga_cli = GAplic('ClientProcess')
        ga_cli.create_gobj('client', GClientPrincipal, None)

        try:
            ga_cli.mt_process()
        except KeyboardInterrupt:
            srv_worker.shutdown()
            srv_worker.join()
            print('Program stopped')

.. _infinite-loop:

Infinite loop
-------------
After create and initialize the :term:`gaplic`, you must call to
the :meth:`ginsfsm.gaplic.GAplic.mt_process` function.
It's the infinite loop where events, timers, etc are processed.

Extra work in the main loop
---------------------------

You can subclass :class:`ginsfsm.gaplic.GAplic` and override
the :meth:`ginsfsm.gaplic.GAplic.mt_subprocess` function to do extra work
in the infinite loop.

Using GObjs
===========

.. _creating-gclass:

Creating new gclass types
-------------------------

To create a new :term:`gclass` type:

#. Write a :term:`simple-machine`.
#. Subclass the :class:`ginsfsm.gobj.GObj` class.
#. Override the :meth:`ginsfsm.gobj.GObj.start_up` method.

See :mod:`ginsfsm.smachine` module to learn how to build
a :term:`simple-machine`::

    class MyGClass(GObj):
        def __init__(self):
            super(MyGClass, self).__init__(SAMPLE_FSM)

        def start_up(self):
            """ Create gobj childs, initialize something...
            """

.. _creating-gobj:

Creating gobjs
--------------

Creating :term:`gobj`'s must be done by
the :meth:`ginsfsm.gaplic.GAplic.create_gobj` factory function
of :class:`ginsfsm.gaplic.GAplic` class, because all :term:`gobj`'s belongs
to a :term:`gaplic`'s domain:

The communication between :term:`gobj`'s are through :term:`event`'s.
The :term:`event`'s are sent from one :term:`gobj` to another :term:`gobj` using
one of these functions:

    * sending events by direct delivery: :ref:`send-event`.
    * sending events by queues: :ref:`post-event`.
    * sending events to subscribers: :ref:`broadcast-event`.

.. _creating-event:

Creating events
---------------

An :term:`event` can be:

* any string name defined in the :term:`simple-machine`'s :term:`event-list`:

    * Used in :ref:`send-event` method.

* any instance of :class:`ginsfsm.gobj.Event` class.
  This class is nothing more than a collection of event attributes:

    * Used in :ref:`post-event` and :ref:`broadcast-event` methods.
      You can to use the :func:`ginsfsm.gobj.event_factory` factory function to
      create :term:`event`'s:

.. _sending-events:

Sending events
--------------

There are three ways to send an event:

* :ref:`send-event`.
* :ref:`post-event`.
* :ref:`broadcast-event`.

.. _send-event:

send_event
^^^^^^^^^^

Send **right now** the :term:`event-name` to the destination gobj,
with associated data.

This event has only one :term:`gobj` destination.

The returned value is the return value from the executed action.

See :meth:`ginsfsm.gobj.GObj.send_event`.

.. _post-event:

post_event
^^^^^^^^^^

Send an :term:`event` in the **next cycle** of the :term:`gaplic` infinite loop.

This event has only one :term:`gobj` destination.

See :meth:`ginsfsm.gobj.GObj.post_event`.

.. _broadcast-event:

broadcast_event
^^^^^^^^^^^^^^^

Broadcast the :term:`event` to all subscribers.

This is a more general function than send_event or post_event.
It's useful when you don't have a direct relation with the :term:`gobj` to whom
send the event.

See :meth:`ginsfsm.gobj.GObj.broadcast_event`.

.. _receiving-events:

Receving events
---------------

You can receive events directy from gobj childs, or from any gobj by
subscription mode.

.. _subscription:

Subcription
^^^^^^^^^^^

You can receive the events of an :term:`gobj` by subscribing them using
the function :meth:`ginsfsm.gobj.GObj.subscribe_event`:

.. _filtering-events:

Filtering events
^^^^^^^^^^^^^^^^

You can set a filter function
with :meth:`ginsfsm.gobj.GObj.set_owned_event_filter` method to check is
some subscriptor wants to own the event.

The function will be used to check the returned value of an :term:`action`.
If the returned value by owned_event_filter function is ``True``,
the :func:`ginsfsm.gobj.GObj.broadcast_event` function doesn't continue
sending the event to other subscribers.
