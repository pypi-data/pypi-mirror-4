# -*- encoding: utf-8 -*-
"""
These module provides support for:

* creating new derived :class:`GObj` class with your
  :term:`simple-machine`.
* creating :term:`gobj`'s with :func:`create_gobj` factory function.

The :class:`GObj` class provides support for:

* sending events:

    * sending events by direct delivery: :meth:`GObj.send_event`.
    * sending events by queues: :meth:`GObj.post_event`.
    * sending events to subscribers: :meth:`GObj.broadcast_event`.

* receiving events:

    * directly from another :term:`gobj`'s who knows you.
    * subscribing to events by the :meth:`GObj.subscribe_event` method.
    * you can filtering events being broadcasting with
      :meth:`GObj.set_owned_event_filter` method.

.. autoclass:: Event
    :members:

.. autoclass:: GObj
    :members: start_up, create_gobj, destroy_gobj,
        send_event, post_event, broadcast_event,
        subscribe_event, delete_subscription, set_owned_event_filter,
        find_unique_gobj,
        overwrite_parameters, overwrite_few_parameters

    .. attribute:: name

        My name.

        Set by :meth:`create_gobj`.

    .. attribute:: parent

        My parent, destination of my events... or not.

        Set by :meth:`create_gobj`.

    .. attribute:: dl_childs

        Set of my gobj childs. Me too like be parent!.


    .. method:: set_new_state

        Set a new state.
        Method to used inside actions, to force the change of state.

        :param new_state: new state to set.

        ``new_state`` must match some of the state names of the
        machine's :term:`state-list` or a :exc:`StateError` exception
        will be raised.

    .. method:: get_current_state

        Return the name of the current state.

        If there is no state it returns ``None``.

    .. method:: get_input_event_list

       Return the list with the :term:`input-event`'s names.

    .. method:: get_output_event_list

       Return the list with the :term:`output-event`'s names.


.. autoexception:: ParentError

.. autoexception:: DestinationError

.. autoexception:: GObjError

.. autoexception:: EventError

.. autoexception:: StateError

.. autoexception:: MachineError

.. autoexception:: EventNotAcceptedError

.. autoexception:: QueueError

"""
import threading
import logging
import ginsfsm.globals  # made it import available

from ginsfsm.compat import string_types

from ginsfsm.smachine import (
    SMachine,
    EventError,
    EventNotAcceptedError,  # made it import available
    StateError,  # made it import available
    MachineError,  # made it import available
)

from ginsfsm.gconfig import (
    GConfig,
    add_gconfig,
)


class ParentError(Exception):
    """ Raised when parent is already defined."""


class DestinationError(Exception):
    """ Raised when destination is not know."""


class GObjError(Exception):
    """ Raised when an object is not a GObj type, and must be!."""


class NotUniqueGObjError(Exception):
    """ Raised when an named object is not the unique gobj."""


class QueueError(Exception):
    """ Raised when there is no support for enqueue objs, i.e., use of
        GObj.post_event() method.
    """


class Event(object):
    """ Collect event properties. This is the argument received by actions.

    :param destination: destination gobj whom to send the event.
    :param event_name: event name.
    :param source: list with path of gobj sources. Firt item ``source[0]``
        is the original sender gobj. Last item ``source[-1]`` is the
        nearest sender gobj.
    :param kw: keyword arguments with associated data to event.
    """
    # For now, event_factory is private. Automatically using by send_event...
    #Use the :meth:`GObj.event_factory` factory function to create Event
    #instances.
    def __init__(self, destination, event_name, source, **kw):
        self.destination = destination
        self.event_name = event_name
        if not isinstance(source, (list, tuple)):
            source = [source]
        self.source = source
        self.kw = kw
        self.__dict__.update(**kw)

    def __str__(self):
        return 'Event object: name %s, destination: %s, kw: %s' % (
            self.event_name,
            self.destination,
            self.kw,
        )


class _Subscription(object):
    """ Collect subscriber properties
    `event_name`: event name.
    `subscriber_gobj`: subcriber gobj to sending event.
    `kw`: event parameters
    """
    def __init__(self, event_name, subscriber_gobj, **kw):
        self.event_name = event_name
        self.subscriber_gobj = subscriber_gobj
        self.kw = kw
        self.__dict__.update(**kw)


# Attributes that a gaplic can update.
GOBJ_GCONFIG = {
    'gaplic': [None, None, 0, None, ''],
    'ini_settings': [dict, {}, 0, None,
        'The ini settings will be set to all new created gobj'
        ' by overwrite_parameters() function'],
    # trace_mach is inherited from SMachine.
    'trace_mach': [bool, False, 0, None, 'Display simple machine activity'],
    # logger is inherited from SMachine.
    'logger': [None, None, 0, None, ''],
    'create_gobj': [None, None, 0, None, ''],
    'enqueue_event': [None, None, 0, None, ''],
    'get_named_gobjs': [None, None, 0, None, ''],
    'register_unique_gobj': [None, None, 0, None, ''],
    'deregister_unique_gobj': [None, None, 0, None, ''],
    'find_unique_gobj': [None, None, 0, None, ''],
    'delete_all_references': [None, None, 0, None, ''],
    '_increase_inside': [None, None, 0, None, ''],
    '_decrease_inside': [None, None, 0, None, ''],
    '_tab': [None, None, 0, None, ''],
}

_urandom_name = 0


class GObj(SMachine, GConfig):
    """ Well, yes, I'm a very simple brain. Only a machine.
    But write a good FSM, and I never fail you. Derive me, and write my FSM.

    Sample GObj::

        class MyGObj(GObj):
            def __init__(self):
                GObj.__init__(self, FSM, GCONFIG)

            def start_up(self):
                ''' Initialization zone.'''

    :param fsm: FSM :term:`simple-machine`.
    :param gconfig: GCONFIG :term:`gconfig-template`.
    """

    def __init__(self, fsm, gconfig=None):
        SMachine.__init__(self, fsm)
        self.name = ''
        """ My name.
        Set by :meth:`create_gobj`
        """
        self.parent = None
        """My parent, destination of my events... or not.
        Set by :meth:`create_gobj`
        """
        self.dl_childs = set()        # my childs... me too like be parent.
        """List of gobj childs.
        """
        self.owned_event_filter = None  # TODO debe ser una lista de filtros
        """Filter to broadcast_event function to check the owner of events.
        """

        self._dl_subscriptions = set()      # uauuu, how many fans!!
        self._some_subscriptions = False
        self._destroyed = False  # mark as destroyed when destroy_gobj()

        gconfig = add_gconfig(gconfig, GOBJ_GCONFIG)
        GConfig.__init__(self, gconfig)

    def __str__(self):
        return "%s:%s" % (self.__class__.__name__, self.name)

    def create_gobj(self, name, gclass, parent, **kw):
        """ Factory function to create gobj's instances.

        :param name: Name of gobj. If it's a :term:`named-gobj` then the
            :meth:`GObj.register_unique_gobj` will be called.
            :meth:`GObj.register_unique_gobj` is a empty method that
            must be override by a superior domain like :term:`gaplic`.
            If :meth:`GObj.register_unique_gobj` fails, a
            :exc:NotUniqueGObjError exception will be raised.
        :param gclass: `gclass` is the :class:`GObj` type used to create
            the new gobj. It's must be a derived class of :class:`GObj`
            otherwise a :exc:`GObjError` exception will be raised.
        :param parent: parent of the new :term:`gobj`. ``None`` if it has no
            parent. It it's not ``None``, then must be a derived class
            of :class:`GObj` otherwise a :exc:`GObjError`
            exception will be raised.
        :param kw: Attributes that are added to the new :term:`gobj`.
            All the keyword arguments used in the function
            **are added as attributes** to the created :term:`gobj`.
            You must consult the attributes supported
            by each `gclass` type.
        :rtype: new gobj instance.

        The factory funcion does:

        * Add the :term:`gobj` to their parent child list
          :attr:`GObj.dl_childs`,
        * If it's a :term:`named-gobj` call the
          :meth:`GObj.register_unique_gobj`.
        * Call :meth:`GObj.start_up`.
        * Add to the :term:`gobj` several attributes:

            * **name**: name of the created :term:`gobj`.
            * **parent**: the parent :term:`gobj` of the created :term:`gobj`.

        .. warning:: the :meth:`GObj.register`, :meth:`GObj.deregister`
            and :meth:`GObj.search` methods must be override and supplied by a
            superior instance, like :term:`gaplic`,
            otherwise :term:`named-gobj` objects cannot be used.
        """

        if gclass is None:
            raise GObjError(
                '''ERROR create_gobj(): No GObj class supplied.''')
        if not issubclass(gclass, GObj):
            raise GObjError(
                '''ERROR create_gobj(): class '%s' is NOT a GObj subclass''' % (
                    repr(gclass)))

        if parent is not None:
            if not isinstance(parent, GObj):
                raise GObjError(
                    '''ERROR create_gobj(): parent '%s' '''
                    '''is NOT a GObj subclass''' % (
                        repr(gclass)))

        if name and self.logger:
            self.logger.debug("Creating named-gobj '%s'" % name)

        gobj = gclass()

        if name:
            gobj.name = name
            registered = self.register_unique_gobj(gobj)
            if not registered:
                raise NotUniqueGObjError(
                    '''ERROR create_gobj():'''
                    ''' cannot register_unique_gobj '%s' ''' % (name))

        # Who wins? arguments or file ini settings?
        gobj.write_parameters(**kw)
        if self.ini_settings is not None:
            # ini global win.
            gobj.overwrite_parameters(0, **self.ini_settings)

        if parent is not None:
            parent._add_child(gobj)

        gobj.start_up()

        return gobj

    def get_random_name(self, prefix):
        global _urandom_name
        _urandom_name += 1
        return '%s_%d' % (prefix, _urandom_name)

    def create_random_named_gobj(self, name, gclass, parent, **kw):
        """ Same as :meth:`create_gobj` function,
        but it generates a random name if name it's not supplied.
        """
        name = self.get_random_name(name)
        return self.create_gobj(name, gclass, parent, **kw)

    def destroy_gobj(self, gobj):
        """ Destroy a gobj
        """
        self.deregister_unique_gobj(gobj)
        if gobj.parent is not None:
            gobj.parent._remove_child(gobj)

        while len(gobj.dl_childs):
            try:
                for child in gobj.dl_childs:
                    self.destroy_gobj(child)
            except RuntimeError:
                pass  # "Set changed size during iteration" is OK

        self.delete_all_references(gobj)
        gobj.delete_all_subscriptions()
        gobj._destroyed = True
        del gobj

    def start_up(self):
        """ Initialization zone.

        Well, the __init__ method is used to build the FSM so I need another
        function to initialize the new gobj.
        Please, **override me**, and write here all the code you need to
        start up the machine: create your owns childs, etc.
        This function is called by :meth:`create_gobj`
        after creating the gobj instance.
        """

    def _resolv_destination(self, destination):
        """ Resolv the destination :term:`gobj`.

        :param destination: destination gobj whom to send the event.
        :rtype: Return the destination :term:`gobj` instance.

        If ``destination`` is a `string`then
        it will be search in the current :term:`gaplic` domain
        with :meth:`find_unique_gobj` method.
        If it is not found a :exc:`DestinationError` exception will be raised.
        """
        if not (isinstance(destination, string_types) or
                isinstance(destination, GObj)):
            raise DestinationError(
                '_resolv_destination() BAD TYPE destination %s in (%s:%s)' %
                (repr(destination), self.__class__.__name__, self.name))

        if isinstance(destination, string_types):
            named_gobj = self.find_unique_gobj(destination)
            if not named_gobj:
                raise DestinationError(
                    '_resolv_destination() destination %s NOT FOUND in (%s:%s)'
                    '\nCurrent named-gobjs: %s'
                    % (repr(destination),
                       self.__class__.__name__,
                       self.name,
                       ' '.join(sorted(self.get_named_gobjs())),
                       )
                    )
            destination = named_gobj
        return destination

    def _event_factory(self, destination, event, **kw):
        """ Factory to create Event instances.

        :param destination: destination gobj whom to send the event.
        :param event: an :term:`event`.
        :param kw: keyword arguments with associated data to event.
        :rtype: Return Event instance.

        ``event`` must be a `string` or :class:`Event` types, otherwise a
        :exc:`EventError` will be raised.

        If ``event`` is an :class:`Event` instance, a new :class:`Event`
        duplicated instance is returned, but it will be updated with
        the new ``destination`` and ``kw`` keyword arguments.

        .. note::
            All the keyword arguments used in the factory function
            **are added as attributes** to the created :term:`event` instance.
            You must consult the attributes supported by each machine's event.
        """
        if not (isinstance(event, string_types) or
                isinstance(event, Event)):
            raise EventError('_event_factory() BAD TYPE event %s in (%s:%s)' %
                (repr(event), self.__class__.__name__, self.name))

        # if destination is not None:
        if not (isinstance(destination, string_types) or
                isinstance(destination, GObj)):
            raise DestinationError(
                '_event_factory() BAD TYPE destination %s in (%s:%s)' %
                (repr(destination), self.__class__.__name__, self.name))

        if isinstance(event, Event):
            # duplicate the event
            if event.source[-1] != self:
                event.source.append(self)
            event = Event(event.destination, event.event_name,
                    event.source, **event.kw)
            if len(kw):
                event.__dict__.update(**kw)
            if destination is not None:
                event.destination = destination
        else:
            event = Event(destination, event, self, **kw)

        return event

    def send_event(self, destination, event, **kw):
        """
        Send **right now** the :term:`event` ``event`` to the
        destination gobj ``destination``, with associated data ``kw``.

        :param event: :term:`event` to send.
        :param destination: destination :term:`gobj` of the event.
        :param kw: keyword argument with data associated to event.
        :rtype: return the returned value from the executed action.

            .. note::
                All the keyword arguments **are added as attributes** to
                the sent :term:`event`.

        If ``event`` argument is a string type, then the internal
        :func:`_event_factory` function  is called, to create a :class:`Event`
        instance.

        The algorithm to calculate the destination :term:`gobj` will be:

            1. ``destination`` if the ``destination`` argument is not ``None``.
            2. ``event.destination`` if ``event`` is a Event instance and
               ``event.destination`` is not ``None``.
            3. If ``destination`` and ``event.destination`` is None, then
               a :exc:`DestinationError` exception will be raised.

        If the :term:`event-name` exists in the machine, but it's not accepted
        by the current state, then no exception is raised but the
        function **returns** :exc:`EventNotAcceptedError`.

            .. note:: The :meth:`inject_event` method doesn't
                **raise** :exc:`EventNotAcceptedError` because a :term:`machine`
                should run under any circumstances. In any way an action can
                raise exceptions.

        If ``destination`` is a :term:`named-gobj`, i.e. a string, then the gobj
        will be search with :meth:`search_gobj` method. This method must be
        supplied and override by superior instance, like :term:`gaplic`.

        ``destination`` must be a `string` or :class:`GObj` types, otherwise a
        :exc:`GObjError` will be raised.

        If ``destination`` if the recipient runs
        in another :term:`gaplic` that the sender,
        the :meth:`post_event` method will be used.

        ``event`` must be a `string` or :class:`Event` types, otherwise a
        :exc:`EventError` will be raised.

        If ``event`` is an :class:`Event` instance, a new :class:`Event`
        duplicated instance is returned, but it will be updated with
        the new ``destination`` and ``kw`` keyword arguments.

        .. note::
            All the keyword arguments used in the factory function
            **are added as attributes** to the created :term:`event` instance.
            You must consult the attributes supported by each machine's event.
        """
        destination = self._resolv_destination(destination)
        event = self._event_factory(destination, event, **kw)
        if destination._destroyed:
            logging.error("GObj ERROR internal: "
                "sending event %s to a destroyed gobj", event.event_name
            )
            return -1

        if self.gaplic:
            cur_ident = threading.current_thread().ident
            cur_name = threading.current_thread().name
            if self.gaplic.thread_ident and cur_ident != self.gaplic.thread_ident:
                logging.error("ERROR internal: "
                    "current thread '%s' is not the sender thread '%s'",
                    cur_name, self.gaplic.thread_name
                )

            dst_ident = destination.gaplic.thread_ident
            if dst_ident and cur_ident != dst_ident:
                return self.post_event(destination, event)

        ret = destination.inject_event(event)
        return ret

    def post_event(self, destination, event, **kw):
        """ Post the event in the event queue. To use with domains like
        :term:`gaplic` because it's necessary to override :meth:`enqueue_event`
        in order to supply a queue system.

        :param event: :term:`event` to send.
        :param destination: destination :term:`gobj` of the event.
        :param kw: keyword argument with data associated to event.

            .. note::
                All the keyword arguments **are added as attributes** to
                the sent :term:`event`.

        ``destination`` must be a `string` or :class:`GObj` types, otherwise a
        :exc:`GObjError` will be raised.

        ``event`` must be a `string` or :class:`Event` types, otherwise a
        :exc:`EventError` will be raised.

        If ``event`` is an :class:`Event` instance, a new :class:`Event`
        duplicated instance is returned, but it will be updated with
        the new ``destination`` and ``kw`` keyword arguments.

        .. note::
            All the keyword arguments used in the factory function
            **are added as attributes** to the created :term:`event` instance.
            You must consult the attributes supported by each machine's event.
        """
        event = self._event_factory(destination, event, **kw)
        self.enqueue_event(event)

    def enqueue_event(self, event):
        """ Enqueue a event to send by queue system.
        To be overriden by :term:`gaplic` or similar
        """
        raise QueueError(
              'enqueue_event() no support in (%s:%s)' % (
              self.__class__.__name__, self.name))

    def broadcast_event(self, event, **kw):
        """ Broadcast the ``event`` to all subscribers.

        :param event: :term:`event` to send.
        :param kw: keyword argument with data associated to event.

            .. note::
                All the keyword arguments **are added as attributes** to
                the sent :term:`event`.

        Use this function when you don't know who are your event's clients,
        when you don't know the :term:`gobj` destination of
        your :term:`output-event`'s

        If there is no subscriptors, the event is not sent.

        When an event has several subscriptors, there is a mechanism called
        :term:`event-filter` that allows to a subcriptor to own the event
        and no further spread by more subscribers.

        The filter function set by :meth:`set_owned_event_filter` method,
        is call with the returned value of an :term:`action` as argument:
        If the filter function return ``True``, the event is owned, and the
        :func:`ginsfsm.gobj.GObj.broadcast_event` function doesn't continue
        sending the event to other subscribers.

        .. note:: If :func:`ginsfsm.gobj.GObj.broadcast_event` function
           uses :func:`ginsfsm.gobj.GObj.post_event`,
           the :term:`event-filter` cannot be applied.
        """
        if self._some_subscriptions:
            subscriptions = self._dl_subscriptions.copy()
            sended_gobj = set()  # don't repeat events
            for sub in subscriptions:
                if sub.subscriber_gobj in sended_gobj:
                    continue

                oevent = self._event_factory(sub.subscriber_gobj, event, **kw)
                if None in sub.event_name or \
                        oevent.event_name in sub.event_name:

                    if hasattr(sub, 'change_original_event_name'):
                        oevent.name = sub.change_original_event_name

                    if hasattr(sub, 'use_post_event'):
                        ret = self.post_event(sub.subscriber_gobj, oevent)
                    else:
                        ret = self.send_event(sub.subscriber_gobj, oevent)
                    sended_gobj.add(sub.subscriber_gobj)
                    if self.owned_event_filter:
                        ret = self.owned_event_filter(ret)
                        if ret is True:
                            return True  # propietary event, retorno otra cosa?

    def subscribe_event(self, event_name, subscriber_gobj, **kw):
        """ Subscribe to event.

        :param event_name: string event name or tuple/list of string
            event names.  If ``event_name`` is ``None`` then it subscribe
            to all events. If it's not ``None`` then it must be a valid event
            name from the :term:`output-event` list,
            otherwise a :exc:`EventError` will be raised.
        :param subscriber_gobj: subscriber obj that wants receive the event.
            If ``subscriber`` is ``None`` then the subscriber is the parent.
            ``subscriber_gobj`` must be `None` or a `string` or a
            :class:`GObj` types, otherwise a :exc:`GObjError` will be raised.
        :param kw: keyword argument with data associated to subscription.

        **kw** values:
            * `use_post_event`:
              You must set it to `True` in order to broadcast the events
              using `post-event` instead of `send-event`.

            * `change_original_event_name`:
              You can change the output original event name..

        """
        if subscriber_gobj is None:
            subscriber_gobj = self.parent

        if subscriber_gobj is not None:
            if not (isinstance(subscriber_gobj, string_types) or
                    isinstance(subscriber_gobj, GObj)):
                raise GObjError(
                    'subcribe_event(): BAD TYPE subscriber_gobj %s in (%s:%s)' %
                    (repr(subscriber_gobj), self.__class__.__name__, self.name))

            if isinstance(subscriber_gobj, string_types):
                named_gobj = self.find_unique_gobj(subscriber_gobj)
                if not named_gobj:
                    raise GObjError(
                        'subscribe_event() subscriber NOT FOUND in (%s:%s)'
                        '\nCurrent named-gobjs: %s'
                        % (self.__class__.__name__,
                           self.name,
                           ' '.join(sorted(self.get_named_gobjs())),
                           )
                        )
                subscriber_gobj = named_gobj

        output_events = self.get_output_event_list()

        if not isinstance(event_name, (list, tuple)):
            event_name = (event_name,)

        for name in event_name:
            if name is None:
                continue
            if not isinstance(name, string_types):
                raise EventError(
                    'subscribe_event(): event %s is not string in (%s:%s)'
                    % (repr(name), self.__class__.__name__, self.name))

            if name not in output_events:
                raise EventError(
                    'subscribe_event(): output-event %s not defined in'
                    ' (%s:%s)' % (
                        repr(event_name),
                        self.__class__.__name__,
                        self.name))

        existing_subs = self._find_subscription(event_name, subscriber_gobj)
        if existing_subs:
            # avoid duplication subscriptions
            self.delete_subscription(event_name, subscriber_gobj)
        subscription = _Subscription(event_name, subscriber_gobj, **kw)
        self._dl_subscriptions.add(subscription)
        self._some_subscriptions = True

    def _find_subscription(self, event_name, subscriber_gobj):
        """ Find a subscription by event_name and subscriber gobj.
        Internal use to avoid duplicates subscriptions.
        """
        if not isinstance(event_name, (list, tuple)):
            event_name = (event_name,)
        for sub in self._dl_subscriptions:
            if list(sub.event_name).sort() == list(event_name).sort() and \
                sub.subscriber_gobj == subscriber_gobj:
                    return sub

    def delete_subscription(self, event_name, subscriber_gobj):
        """ Remove `subscription`.

        :param event_name: string event name or tuple/list of string
            event names.
        :param subscriber_gobj: subscriber gobj.
        """
        existing_subs = self._find_subscription(event_name, subscriber_gobj)
        if existing_subs:
            self._dl_subscriptions.remove(existing_subs)
            if len(self._dl_subscriptions) == 0:
                self._some_subscriptions = False
            return True
        logging.error("ERROR delete_subscription(): '%s' NOT FOUND " %
            event_name)

        return False

    def delete_all_subscriptions(self):
        """ Remove all subscriptions.
        """
        while len(self._dl_subscriptions):
            try:
                for subs in self._dl_subscriptions:
                    self._dl_subscriptions.remove(subs)
            except RuntimeError:
                pass  # "Set changed size during iteration" is OK

    def set_owned_event_filter(self, filter):
        """ Set a filter function to be used by :meth:`broadcast_event` function
        to check the owner of events.
        """
        self.owned_event_filter = filter

    def get_named_gobjs(self):
        """ Return the list of :term:`named-gobj`'s.
        To be overriden by :term:`gaplic` or similar.
        """
        return []

    def register_unique_gobj(self, gobj):
        """ Register a :term:`named-gobj`.
        To be overriden by :term:`gaplic` or similar.
        """
        return True

    def deregister_unique_gobj(self, gobj):
        """ Deregister a :term:`named-gobj`.
        To be overriden by :term:`gaplic` or similar.
        """
        return True

    def find_unique_gobj(self, gobj_name):
        """ Find a :term:`named-gobj`.
        To be overriden by :term:`gaplic` or similar.
        """
        return None

    def delete_all_references(self, gobj):
        """ Delete all references of gobj in upper levels (ex: queues).
        Call when the gobj is destroyed.
        To be overriden by :term:`gaplic` or similar.
        """

    def _add_child(self, gobj):
        """ Add a child ``gobj``.

        :param gobj: :term:`gobj` child to add.

        Raise :exc:`ParentError` is ``gobj`` already has a parent.
        This function is called by :meth:`create_gobj`
        after creating the gobj instance.
        """
        if gobj.parent:
            raise ParentError(
                '_add_child(): gobj already has parent in (%s:%s)' %
                (self.__class__.__name__, self.name))
        self.dl_childs.add(gobj)
        gobj.parent = self

    def _remove_child(self, gobj):
        """ Remove the child ``gobj``.

        :param gobj: :term:`gobj` child to remove.

        This function is called by :meth:`destroy_gobj`.
        """
        if gobj in self.dl_childs:
            self.dl_childs.remove(gobj)
            gobj.parent = None

    def __getitem__(self, name):
        """ Enable gobjs tree to work with Pyramid trasversal URL dispatch.
        """
        if name is None:
            raise KeyError('No such child named None')
        for gobj in self.dl_childs:
            if gobj.name == name:
                return gobj
        raise KeyError('No such child named %s' % name)

    def __iter__(self):
        """ Iterates over child elements.
        """
        return self.dl_childs.__iter__()

    def overwrite_parameters(self, level, **settings):
        """ The parameters in settings must be defined in the gobj.

        :param level: level trace of childs.
            indicates the depth of the childs as far to change.

            * `0` only this gobj.
            * `-1` all tree of childs.

        :param settings: parameters and their values.

        The settings are filtered by the named-gobj or gclass name of this gobj.
        The parameter name in settings, must be a dot-named,
        with the first item being the named-gobj o gclass name.
        """
        parameters = self.filter_parameters(**settings)
        self.write_parameters(**parameters)
        if level:
            for child in self.dl_childs:
                child.overwrite_parameters(level - 1, **settings)

    def overwrite_few_parameters(self, parameter_list, **settings):
        """ The parameters in settings must be defined in the gobj.

        :param parameter_list: write only the parameters in ``parameter_list``.

        :param settings: parameters and their values.

        The settings are filtered by the named-gobj or gclass name of this gobj.
        The parameter name in settings, must be a dot-named,
        with the first item being the named-gobj o gclass name.
        """
        parameters = self.filter_parameters(**settings)
        self.write_few_parameters(parameter_list, **parameters)
