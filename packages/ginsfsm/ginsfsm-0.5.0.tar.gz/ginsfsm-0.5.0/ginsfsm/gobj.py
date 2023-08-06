# -*- encoding: utf-8 -*-
"""
Introduction
============

An :term:`GObj` is an object that has an inside :term:`simple-machine`
that defines its behavior.

The communication between :term:`gobj`'s happens via :term:`event`'s:

:class:`GObj` has the next methods:

* :meth:`GObj.start_up`
* :meth:`GObj.create_gobj`
* :meth:`GObj.destroy_gobj`
* :meth:`GObj.send_event`
* :meth:`GObj.post_event`
* :meth:`GObj.broadcast_event`
* :meth:`GObj.subscribe_event`
* :meth:`GObj.delete_subscription`
* :meth:`GObj.set_owned_event_filter`
* :meth:`GObj.overwrite_parameters`
* :meth:`GObj.overwrite_few_parameters`

And this inherited from :class:`ginsfsm.smachine.SMachine`:

* :meth:`ginsfsm.smachine.SMachine.set_new_state`
* :meth:`ginsfsm.smachine.SMachine.get_current_state`
* :meth:`ginsfsm.smachine.SMachine.get_event_list`
* :meth:`ginsfsm.smachine.SMachine.get_output_event_list`


:class:`GObj` has the next public attributes:

* :attr:`GObj.name`
* :attr:`GObj.parent`
* :attr:`GObj.dl_childs`

Events to manage events:

* sending events:

    * sending events by direct delivery: :meth:`GObj.send_event`.
    * sending events by queues: :meth:`GObj.post_event`.
    * sending events to subscribers: :meth:`GObj.broadcast_event`.

* receiving events:

    * directly from another :term:`gobj`'s who knows you.
    * subscribing to events by the :meth:`GObj.subscribe_event` method.
    * you can filtering events being broadcasting with
      :meth:`GObj.set_owned_event_filter` method.


Event
=====

.. autoclass:: Event
    :members:


GObj
====

.. autoclass:: GObj
    :members: start_up, create_gobj, destroy_gobj,
        send_event, post_event, broadcast_event,
        subscribe_event, delete_subscription, set_owned_event_filter,
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

    .. method:: get_event_list

       Return the list with the :term:`input-event`'s names.

    .. method:: get_output_event_list

       Return the list with the :term:`output-event`'s names.


Exceptions
==========

.. autoexception:: GObjError

.. autoexception:: EventError

.. autoexception:: StateError

.. autoexception:: MachineError

.. autoexception:: EventNotAcceptedError

"""
import re
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
from ginsfsm.deferred import Deferred


class GObjError(Exception):
    """ General GObj exception"""


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
        self.kw = kw.copy()
        self.__dict__.update(**kw)

    def copy(self):
        pass

    def __repr__(self):
        return 'Event object: name %r, destination: %r, kw: %r' % (
            self.event_name,
            self.destination,
            self.kw,
        )

    def __str__(self):
        return 'Event object: name %r, destination: %r, kw: %r' % (
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
    def __init__(self, me, event_name, subscriber_gobj, **kw):
        self.me = me
        self.event_name = event_name
        self.subscriber_gobj = subscriber_gobj
        self.kw = kw
        self.__dict__.update(**kw)

    def __repr__(self):
        resp = "Subscription:\n  me : %r\n  ev : %r\n  sub: %r\n" % (
            self.me,
            self.event_name,
            self.subscriber_gobj)
        return resp


GOBJ_GCONFIG = {
    'trace_traverse': [bool, False, 0, None, 'Trace traverse search'],
    'trace_creation': [
        bool, False, GConfig.FLAG_DIRECT_ATTR, None,
        'Trace creation/destroy of gobj'],
    'trace_subscription': [bool, False, 0, None, 'Trace event subscribing'],
    're_name': [
        str, None, 0, None,
        'Regular expression name to search the gobj in the resource tree.'
        'Used in Pyramid traversal.'],

    # trace_mach is inherited from SMachine.
    'trace_mach': [
        bool, False, GConfig.FLAG_DIRECT_ATTR, None,
        'Trace machine activity'
    ],
    # logger is inherited from SMachine.
    'logger': [None, None, GConfig.FLAG_DIRECT_ATTR, None, ''],

    'gaplic': [None, None, GConfig.FLAG_DIRECT_ATTR, None, 'My grand-father'],
    'create_gobj': [None, None, GConfig.FLAG_DIRECT_ATTR, None, ''],
    'destroy_gobj': [None, None, GConfig.FLAG_DIRECT_ATTR, None, ''],
    '_increase_inside': [None, None, GConfig.FLAG_DIRECT_ATTR, None, ''],
    '_decrease_inside': [None, None, GConfig.FLAG_DIRECT_ATTR, None, ''],
    '_tab': [None, None, GConfig.FLAG_DIRECT_ATTR, None, ''],
    '__unique_name__': [
        bool, False, GConfig.FLAG_DIRECT_ATTR, None,
        'If using gaplic, unique name'
    ],
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

    # name and parent attributes must be Location-Aware Resources
    # for Pyramid framework compatibility:
    # changed to point to __name__ and __parent__.
    @property
    def name(self):
        return self.__name__

    @name.setter
    def name(self, name):
        self.__name__ = name

    @property
    def parent(self):
        return self.__parent__

    @parent.setter
    def parent(self, parent):
        self.__parent__ = parent

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
        self._re_compiled_name = ''  # re compiled name when using re_name
        self.re_matched_name = ''  # matched name when using re_name
        self.trace_creation = False
        gconfig = add_gconfig(gconfig, GOBJ_GCONFIG)
        GConfig.__init__(self, gconfig, self.logger)

    def __del__(self):
        if self.trace_creation:
            self.logger and self.logger.info("Destroyed! <-- %r" % (self))

    def __str__(self):
        name = "%s" % (self.name)
        parent = self.parent
        while(parent):
            parent_name = "%s" % (parent.name)
            name = parent_name + '.' + name
            parent = parent.parent
        return "%s" % (name)

    def __repr__(self):
        name = "%s:%s" % (self.__class__.__name__, self.name)
        parent = self.parent
        while(parent):
            parent_name = "%s:%s" % (parent.__class__.__name__, parent.name)
            name = parent_name + '.' + name
            parent = parent.parent
        return "'%s: %s'" % (name, 'Destroyed' if self._destroyed else "Lived")

    def create_gobj(self, name, gclass, parent, **kw):
        """ Factory function to create gobj's instances.

        :param name: Name of the gobj.

        :param gclass: `gclass` is the :class:`GObj` type used to create
            the new gobj. It's must be a derived class of :class:`GObj`
            otherwise a :exc:`GObjError` exception will be raised.

        :param parent: parent of the new :term:`gobj`. ``None`` if it has no
            parent. If it's not ``None``, then must be a derived class
            of :class:`GObj` otherwise a :exc:`GObjError`
            exception will be raised.

        :param kw: Attributes that are added to the new :term:`gobj`.
            All the keyword arguments used in the creation function
            **are added as attributes** to ``config`` object.

            You must consult the attributes supported
            by each `gclass` type.
            The attributes must be defined in the gclass GCONFIG,
            otherwise they are ignored.

            Special kw:

                ``'__random_name__'``: Generate a random gobj name

            TODO: doc re_name

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
        """

        if gclass is None:
            raise GObjError(
                '''ERROR create_gobj(): No GObj class supplied.''')
        if not issubclass(gclass, GObj):
            raise GObjError(
                '''ERROR create_gobj(): class '%r' is NOT a GObj subclass''' %
                (gclass))

        if parent is not None:
            if not isinstance(parent, GObj):
                raise GObjError(
                    '''ERROR create_gobj(): parent '%r' '''
                    '''is NOT a GObj subclass''' % (gclass))

        self.__random_name__ = kw.pop('__random_name__', False)
        if self.__random_name__:
            name = self.get_random_name(name)

        gobj = gclass()

        if name:
            gobj.name = name

        # Who wins? arguments or file ini_settings?
        # ini global (in gaplic) wins.
        gobj.write_parameters(**kw)
        if self.gaplic and self.gaplic.ini_settings is not None:
            # ini global win.
            gobj.overwrite_parameters(0, **self.gaplic.ini_settings)

        if parent is not None:
            parent._add_child(gobj)

        if gobj.config.re_name:
            gobj._re_compiled_name = re.compile(gobj.config.re_name)

        if gobj.trace_creation:
            self.logger and self.logger.info("Creating --> '%s:%s'" % (
                gclass.__name__, name))

        if gobj.__unique_name__:
            registered = self.gaplic._register_unique_gobj(gobj)
            if not registered:
                raise GObjError(
                    "ERROR create_gobj():"
                    " cannot _register_unique_gobj '%s' " % (gobj.name))

        gobj.start_up()

        if gobj.trace_creation and self.logger:
            if gobj.__unique_name__:
                unique = '!'
            else:
                unique = ' '
            self.logger.info("Created <--%s '%r'" % (unique, gobj))

        return gobj

    def get_random_name(self, prefix):
        global _urandom_name
        _urandom_name += 1
        if prefix:
            return '%s_%d' % (prefix, _urandom_name)
        else:
            return '%d' % (_urandom_name)

    @staticmethod
    def destroy_gobj(gobj):
        """ Destroy a gobj
        """
        if gobj.trace_creation and gobj.logger:
            gobj.logger.info("Destroying --> %r" % (gobj))

        if gobj._destroyed:
            if gobj.logger:
                gobj.logger.error(
                    "ERROR reentering in destroy_gobj: %r" % gobj)
            return

        gobj._destroyed = True
        if gobj.parent is not None:
            gobj.parent._remove_child(gobj)

        while len(gobj.dl_childs):
            try:
                for child in gobj.dl_childs:
                    if not child._destroyed:
                        GObj.destroy_gobj(child)
            except RuntimeError:
                pass  # "Set changed size during iteration" is OK

        gobj.delete_all_subscriptions(force=True)
        gobj.go_out()
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

    def go_out(self):
        """ Finish zone.

        Please, **override me** to do extra work
        when the gobj is being destroyed.

        In this point, all childs and subscriptions are already deleted.
        """

    def _resolv_destination(self, destination):
        """ Resolve the destination gobj.
            If destination it's a string:
                * check is gaplic exists.
                * try to resolv the destination by gaplic.

                If the string destination cannot be resolved
                then return the string. It must be resolved by gaplic router.
        """
        if not (isinstance(destination, (string_types, GObj))):
            raise GObjError(
                'Destination gobj ("%s") must be a string or a GObj instance'
                % (destination)
            )

        if isinstance(destination, string_types):
            if not self.gaplic:
                raise GObjError(
                    'When destination gobj ("%s") is a string, '
                    'you need a GAplic!' % (destination)
                )

            named_gobj = self.gaplic.find_unique_gobj(destination)
            if not named_gobj:
                raise GObjError('GObj %r UNKNOWN in %r' % (
                    destination, self.gaplic))
            destination = named_gobj

        return destination

    def _event_factory(self, destination, event, **kw):
        """ Factory to create Event instances.

        :param destination: destination gobj whom send the event.
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
            raise EventError(
                'Event "%r" must be a string or Event instance' %
                (event,))

        # if destination is not None:
        if not (isinstance(destination, string_types) or
                isinstance(destination, GObj) or
                isinstance(destination, Deferred)
                ):
            raise GObjError(
                'Destination "%r" must be a string or GObj/Deferred instance' %
                (destination,))

        if isinstance(event, Event):
            # duplicate the event
            if event.source[-1] != self:
                event.source.append(self)
            if len(kw):
                event.kw.update(**kw)
            event = Event(
                event.destination,
                event.event_name,
                event.source,
                **event.kw
            )
            if destination is not None:
                event.destination = destination
        else:
            event = Event(destination, event, self, **kw)

        return event

    def send_event(self, destination, event, **kw):
        """
        Send ``event`` to ``destination``, with associated event data ``kw``.

        :param destination: Must be a string gobj name or
            a :term:`gobj` instance,
            otherwise a :exc:`GObjError` will be raised.
            If it's a string and the gobj name cannot be resolved
            inside the current :term:`gaplic`, then the event is
            :func:`post_event` in order to be resolved by the gaplic router.

        :param event: Must be a string event name or a :class:`Event` instance,
            otherwise an :exc:`EventError` will be raised.

        :param kw: All the keyword arguments **are added as attributes** to
            the sent :class:`Event` instance.
            You must consult the attributes supported by each machine's event.

        :rtype: return the returned value from the executed action.
            Return ``None`` if the event has been :func:`post_event`.

        If the :term:`event-name` exists in the machine, but it's not accepted
        by the current state, then no exception is raised but the
        function **returns** :exc:`EventNotAcceptedError`.

        .. note:: The :meth:`inject_event` method doesn't
            **raise** :exc:`EventNotAcceptedError` because a
            :term:`machine` should run under any circumstances.
            In any way an action can raise exceptions.

        """
        destination = self._resolv_destination(destination)
        event = self._event_factory(destination, event, **kw)

        if isinstance(destination, string_types):
            # string gobjs must be resolved by gaplic
            return self.post_event(destination, event)

        if destination._destroyed:
            self.logger and self.logger.error(
                "ERROR internal: sending event %r to a destroyed gobj %r" % (
                    event.event_name, destination)
            )
            return -1

        ret = destination.inject_event(event)
        return ret

    def post_event(self, destination, event, **kw):
        """ Same funcionality as :func:`send_event`,
        but the event is processed by gaplic.
        If the destination is inside of the current gaplic the event will be
        sent in the next loop cycle.
        If the destination is in another gaplic, the event will be processed
        by the gaplic's router.
        """
        event = self._event_factory(destination, event, **kw)
        if not self.gaplic:
            raise GObjError(
                'To use post_event, you need a GAplic!'
            )
        self.gaplic.enqueue_event(event)

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
        if not self._some_subscriptions:
            return
        subscriptions = self._dl_subscriptions.copy()
        sended_gobj = set()  # don't repeat events
        for sub in subscriptions:
            if sub.subscriber_gobj in sended_gobj:
                continue

            oevent = self._event_factory(sub.subscriber_gobj, event, **kw)
            if None in sub.event_name or \
                    oevent.event_name in sub.event_name:

                if hasattr(sub, '__rename_event_name__'):
                    oevent.kw.update(
                        {
                            'original_event_name': oevent.event_name,
                        }
                    )
                    oevent.event_name = sub.__rename_event_name__

                if hasattr(sub, '__subscription_reference__'):
                    oevent.kw.update(
                        {
                            '__subscription_reference__':
                            sub.__subscription_reference__,
                        }
                    )
                    oevent.event_name = sub.__rename_event_name__

                ret = False
                if isinstance(sub.subscriber_gobj, Deferred):
                    # outside world
                    sub.subscriber_gobj(event=oevent)
                else:
                    # gobj-ecosistema
                    if hasattr(sub, '__use_post_event__'):
                        ret = self.post_event(sub.subscriber_gobj, oevent)
                    else:
                        ret = self.send_event(sub.subscriber_gobj, oevent)
                        if self.owned_event_filter:
                            ret = self.owned_event_filter(ret)
                            if ret is True:
                                return  # propietary event
                sended_gobj.add(sub.subscriber_gobj)

    def subscribe_event(self, event_name, subscriber_gobj, **kw):
        """ Subscribe to an event.

        :param event_name: string event name or tuple/list of string
            event names.  If ``event_name`` is ``None`` then it subscribes
            to all events. If it's not ``None`` then it must be a valid event
            name from the :term:`output-event` list,
            otherwise a :exc:`EventError` will be raised.

        :param subscriber_gobj: subscriber obj that wants receive the event.

            ``subscriber_gobj`` must be:
                * `None`: the subscriber is the parent.
                * `string`: the subscriber is a :term:`unique-named-gobj`.
                * type :class:`GObj` instance.
                * Deferred callback.

            otherwise otherwise a :exc:`GObjError` will be raised.

        :param kw: keyword arguments.
        :return: the subscription object.

        Possible values for **kw** arguments:
            * `__use_post_event__`: ``bool``

              You must set it to `True` in order to broadcast the events
              using `post-event` instead of `send-event`.

            * `__rename_event_name__`: `'new event name'`

              You can rename the output original event name.
              The :attr:`original_event_name` attribute is added to
              the sent event with the value of the original event name.


            * `__hard_subscription__`:  ``bool``

              True for permanent subscription.

              This subscription cannot be remove,
              neither with delete_all_subscriptions().
              (Well, with force you can)

            * `__subscription_reference__`:  ``str``

              If exists, it will be added as kw in the event broadcast.
              Can be used by the subscriptor for general purposes.

        """
        #if subscriber_gobj is not None:
        if not (isinstance(subscriber_gobj, string_types) or
                isinstance(subscriber_gobj, Deferred) or
                isinstance(subscriber_gobj, GObj)
                ):
            raise GObjError('Bad type of subscriber_gobj %r' % (
                subscriber_gobj,))

        output_events = self.get_output_event_list()

        if not isinstance(event_name, (list, tuple)):
            event_name = (event_name,)

        for name in event_name:
            if name is None:
                continue
            if not isinstance(name, string_types):
                raise EventError(
                    'subscribe_event(): event %r is not string in %r'
                    % (name, self))

            if name not in output_events:
                raise EventError(
                    'subscribe_event(): output-event %r not defined in'
                    ' %r' % (event_name, self))

        existing_subs = self._find_subscription(event_name, subscriber_gobj)
        if existing_subs:
            # avoid duplication subscriptions
            if self.logger:
                self.logger.warning(
                    "WARNING duplicate subscription:\n"
                    "  me : %r\n"
                    "  ev : %r\n"
                    "  sub: %r\n" %
                    (self, event_name, subscriber_gobj))
            self.delete_subscription(event_name, subscriber_gobj)
        subscription = _Subscription(self, event_name, subscriber_gobj, **kw)
        if self.config.trace_subscription and self.logger:
            self.logger.info('NEW %r' % subscription)
        self._dl_subscriptions.add(subscription)
        self._some_subscriptions = True
        return subscription

    def _find_subscription(self, event_name, subscriber_gobj):
        """ Find a subscription by event_name and subscriber gobj.
        Internal use to avoid duplicates subscriptions.
        """
        if not isinstance(event_name, (list, tuple)):
            event_name = (event_name,)
        for sub in self._dl_subscriptions:
            if sorted(list(sub.event_name)) == sorted(list(event_name)):
                if sub.subscriber_gobj == subscriber_gobj:
                    return sub
        return None

    def delete_subscription_by_object(self, subscription):
        if subscription in self._dl_subscriptions:
            if self.config.trace_subscription and self.logger:
                self.logger.info('DEL %r' % subscription)
            self._dl_subscriptions.remove(subscription)
            if len(self._dl_subscriptions) == 0:
                self._some_subscriptions = False
            return True
        return False

    def delete_subscription(self, event_name, subscriber_gobj):
        """ Remove `subscription`.

        :param event_name: string event name or tuple/list of string
            event names.
        :param subscriber_gobj: subscriber gobj.
        """
        sub = self._find_subscription(event_name, subscriber_gobj)
        if self.config.trace_subscription and self.logger:
            self.logger.info('DEL %r' % sub)
        if sub:
            if sub.kw.get('__hard_subscription__', None):
                if self.logger:
                    self.logger.error(
                        "WARNING cannot delete a hard subscription(): '%s'" % (
                            event_name))
                return False
            else:
                self._dl_subscriptions.remove(sub)
                if len(self._dl_subscriptions) == 0:
                    self._some_subscriptions = False
                return True

        if self.logger:
            self.logger.error(
                "ERROR delete_subscription(): '%s' NOT FOUND " % (event_name))

        return False

    def delete_all_subscriptions(self, force=False):
        """ Remove all subscriptions.
        """
        subscriptions = self._dl_subscriptions.copy()
        for sub in subscriptions:
            if not force:
                if sub.kw.get('__hard_subscription__'):
                    continue

            if self.config.trace_subscription and self.logger:
                self.logger.info('DEL %r' % sub)
            self._dl_subscriptions.remove(sub)

        if len(self._dl_subscriptions) == 0:
            self._some_subscriptions = False

    def set_owned_event_filter(self, filter):
        """ Set a filter function to be used
        by :meth:`broadcast_event` function to check the owner of events.
        """
        self.owned_event_filter = filter

    def _add_child(self, gobj):
        """ Add a child ``gobj``.

        :param gobj: :term:`gobj` child to add.

        Raise :exc:`GObjError` is ``gobj`` already has a parent.
        This function is called by :meth:`create_gobj`
        after creating the gobj instance.
        """
        if gobj.parent:
            raise GObjError('GObj "%r" already has parent' % (gobj))
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
        """ Enable gobjs tree to work with Pyramid traversal URL dispatch.
        """
        trace_traverse = self.config.trace_traverse
        if trace_traverse and self.logger:
            self.logger.debug("==> TRAVERSING('%s') -> %s" % (
                name, self.resource_path()))

        if name is None:
            raise KeyError('Parameter name cannot be None')
        # Firstly search no re_name
        for gobj in self.dl_childs:
            if gobj.config.re_name:
                continue
            else:
                if gobj.name == name:
                    if trace_traverse and self.logger:
                        self.logger.debug("    TRAVERSING FOUND!")
                    return gobj

        # Secondly search re_name
        for gobj in self.dl_childs:
            if gobj.config.re_name:
                if gobj._re_compiled_name.match(name) is not None:
                    # this gobj has been got as re_matched_name.
                    gobj.re_matched_name = name
                    if trace_traverse and self.logger:
                        self.logger.debug("    TRAVERSING %s FOUND RE!" % name)
                    return gobj
            else:
                continue
        if trace_traverse and self.logger:
            self.logger.debug("<== TRAVERSING('%s') -> %s END!" % (
                name, self.resource_path()))
        raise KeyError('No such child named %s' % name)

    def __iter__(self):
        """ Iterates over child elements.
        """
        return self.dl_childs.__iter__()

    # helper for pyramid
    def resource_path(self, separator='/'):
        """ Same as Pyramid traversal.resource_path, but without escaping.
        """
        path = [loc.__name__ or '' for loc in lineage(self)]
        path.reverse()
        return path and separator.join([x for x in path]) or separator

    def overwrite_parameters(self, level, **settings):
        """ The parameters in settings must be defined in the gobj.

        :param level: level trace of childs.
            indicates the depth of the childs as far to change.

            * `0` only this gobj.
            * `-1` all tree of childs.

        :param settings: parameters and their values.

        The settings are filtered by the named-gobj
        or gclass name of this gobj.
        The parameter name in settings, must be a dot-named,
        with the first item being the named-gobj o gclass name.
        """
        parameters = self.filter_parameters(**settings)
        self.write_parameters(**parameters)
        if level > 0:
            for child in self.dl_childs:
                child.overwrite_parameters(level - 1, **settings)

    def overwrite_few_parameters(self, parameter_list, **settings):
        """ The parameters in settings must be defined in the gobj.

        :param parameter_list: write only the parameters in ``parameter_list``.

        :param settings: parameters and their values.

        The settings are filtered by the named-gobj
        or gclass name of this gobj.
        The parameter name in settings, must be a dot-named,
        with the first item being the named-gobj o gclass name.
        """
        parameters = self.filter_parameters(**settings)
        self.write_few_parameters(parameter_list, **parameters)


def inside(resource1, resource2):
    """Is ``resource1`` 'inside' ``resource2``?  Return ``True`` if so, else
    ``False``.

    ``resource1`` is 'inside' ``resource2`` if ``resource2`` is a
    :term:`lineage` ancestor of ``resource1``.  It is a lineage ancestor
    if its parent (or one of its parent's parents, etc.) is an
    ancestor.
    """
    while resource1 is not None:
        if resource1 is resource2:
            return True
        resource1 = resource1.__parent__

    return False


def lineage(resource):
    """
    Return a generator representing the :term:`lineage` of the
    :term:`resource` object implied by the ``resource`` argument.  The
    generator first returns ``resource`` unconditionally.  Then, if
    ``resource`` supplies a ``__parent__`` attribute, return the resource
    represented by ``resource.__parent__``.  If *that* resource has a
    ``__parent__`` attribute, return that resource's parent, and so on,
    until the resource being inspected either has no ``__parent__``
    attribute or which has a ``__parent__`` attribute of ``None``.
    For example, if the resource tree is::

      thing1 = Thing()
      thing2 = Thing()
      thing2.__parent__ = thing1

    Calling ``lineage(thing2)`` will return a generator.  When we turn
    it into a list, we will get::

      list(lineage(thing2))
      [ <Thing object at thing2>, <Thing object at thing1> ]
    """
    while resource is not None:
        yield resource
        # The common case is that the AttributeError exception below
        # is exceptional as long as the developer is a "good citizen"
        # who has a root object with a __parent__ of None.  Using an
        # exception here instead of a getattr with a default is an
        # important micro-optimization, because this function is
        # called in any non-trivial application over and over again to
        # generate URLs and paths.
        try:
            resource = resource.__parent__
        except AttributeError:
            resource = None
