.. _glossary:

Glossary
========

.. glossary::
    :sorted:

    simple-machine
        The `simple-machine` is the argument to
        the :class:`ginsfsm.smachine.SMachine` class.

        It's a simple implementation of an Finite State Machines
        (`FSM <http://en.wikipedia.org/wiki/Finite-state_machine>`_)
        using a *python dictionary with three keys*.

        This is an example from :mod:`ginsfsm.examples.ontimer`::

            ONTIMER_FSM = {
                'event_list': ('EV_TIMEOUT',),
                'state_list': ('ST_STATE',),
                'machine': {
                    'ST_STATE':
                    (
                        ('EV_TIMEOUT', ac_task, 'ST_STATE'),
                    ),
                }
            }

        See :mod:`ginsfsm.smachine` for more details.

    gconfig-template
        The `gconfig-template` is the argument to
        the :class:`ginsfsm.gconfig.GConfig` class.

        It's a *python dictionary*.

        The key is the *parameter name*, and the value is a list describing
        the parameter:

            ``[type, default value, and description]``

        This is an example from :mod:`ginsfsm.examples.ontimer`::

            ONTIMER_GCONFIG = {  # type, default_value, flag, validate_function, desc
                'seconds': [int, 2, 0, None, "Seconds to repeat the command."],
                'verbose': [int, 0, 0, None, "Increase output verbosity."],
                'command': [str, 'ls', 0, None, "Command to execute."],
            }

        See :mod:`ginsfsm.gconfig` for more details.

    gobj
        An instance of :class:`ginsfsm.gobj.GObj` class or derived.

    gaplic
        An instance of :class:`ginsfsm.gaplic.GAplic` class or derived.

        It's the root, the grandfather,

        the container of all :term:`gobj`'s' running in the same thread or
        subprocess.

    event
        It's a :term:`event-name` or any object with a ``event_name`` attribute
        that feeds a :term:`simple-machine`.

        This is how :term:`gobj` communicate with each other: using *events*.

    event-name
        String defining the name of an event.


    create_gobj
        Factory function to create :term:`gobj`'s.
        See :meth:`ginsfsm.gaplic.GAplic.create_gobj`.

    principal
        Any :term:`gobj` created without parent.

    unnamed-gobj
        Unnamed :term:`gobj`.

    named-gobj
        Named :term:`gobj`.

    start_up
        The pseudo **"__init__"** method of the `GObj` class.
        Method of :class:`ginsfsm.gobj.GObj` class to be overried.

    machine
        Value of ``machine`` key of :term:`simple-machine` that is another
        dictionary describing the machine :mod:`ginsfsm.smachine`.


    input-event
        Events that a :term:`gobj` receive from other :term:`gobj`'s,
        or send to itself.

    output-event
        Events that are sent to another :term:`gobj`'s.

    event-filter
        Function for filtering events being broadcasting.

    event-list
        List or tuple of all :term:`input-event`'s event names used in
        the :term:`machine`.

    state-list
        List of state names of the :term:`machine`. No matter the order,
        but it is important the first state, because it is the default state
        when the machine starts.

    action
        Function to be executed when a :term:`machine` receives an :term:`event`.

    next-state
        Name of next state to set in a :term:`machine` when it receives an event.

    state
        State name of a machine's state. We don't difference between `state`
        and `state-name`, as opposite as :term:`event`/:term:`event-name`,
        because there is no a visible `state instance`.
