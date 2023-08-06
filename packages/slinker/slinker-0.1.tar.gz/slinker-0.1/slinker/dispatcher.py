import weakref
import threading

from slinker import saferef

WEAKREF_TYPES = (weakref.ReferenceType, saferef.BoundMethodWeakref)


def _make_id(target):
    if hasattr(target, '__func__'):
        return (id(target.__self__), id(target.__func__))
    return id(target)
NONE_ID = _make_id(None)

# A marker for caching
NO_RECEIVERS = object()


class Link(object):
    """
    Base class for all links

    Internal attributes:

        receivers
            { receriverkey (id) : weakref(receiver) }
    """
    def __init__(self, providing_args=None):
        """
        Create a new link.

        providing_args
            A list of the arguments this link can pass along in a send() call.
        """
        self.receiver = None
        if providing_args is None:
            providing_args = []
        self.providing_args = set(providing_args)
        self.lock = threading.Lock()

    def connect(self, receiver, weak=True):
        """
        Connect receiver to sender for link.

        Arguments:

            receiver
                A function or an instance method which is to receive links.
                Receivers must be hashable objects.

                If weak is True, then receiver must be weak-referencable (more
                precisely saferef.safeRef() must be able to create a reference
                to the receiver).

                Receivers must be able to accept keyword arguments.

                If receivers have a dispatch_uid attribute, the receiver will
                not be added if another receiver already exists with that
                dispatch_uid.


            weak
                Whether to use weak references to the receiver. By default, the
                module will attempt to use weak references to the receiver
                objects. If this parameter is false, then strong references will
                be used.
        """
        if self.receiver:
            raise TypeError("a link can only has a single receiver")

        lookup_key = _make_id(receiver)

        if weak:
            receiver = saferef.safeRef(
                receiver, onDelete=self._remove_receiver)

        with self.lock:
            self.receiver = lookup_key, receiver

    def disconnect(self, receiver=None, weak=True):
        """
        Disconnect receiver from sender for link.

        If weak references are used, disconnect need not be called. The receiver
        will be remove from dispatch automatically.

        Arguments:

            receiver
                The registered receiver to disconnect. May be none if
                dispatch_uid is specified.

            sender
                The registered sender to disconnect

            weak
                The weakref state to disconnect

        """
        lookup_key = _make_id(receiver)

        with self.lock:
            r_key, _ = self.receiver
            if r_key == lookup_key:
                self.receiver = None

    def send(self, sender, **named):
        """
        Send link from sender to all connected receivers.

        If any receiver raises an error, the error propagates back through send,
        terminating the dispatch loop, so it is quite possible to not have all
        receivers called if a raises an error.

        Arguments:

            sender
                The sender of the link Either a specific object or None.

            named
                Named arguments which will be passed to receivers.

        Returns a list of tuple pairs [(receiver, response), ... ].
        """
        if not self.receiver:
            return None, None

        _, weak_receiver = self.receiver
        receiver = weak_receiver()
        response = receiver(link=self, sender=sender, **named)
        return receiver, response

    def send_robust(self, sender, **named):
        """
        Send link from sender to all connected receivers catching errors.

        Arguments:

            sender
                The sender of the link. Can be any python object (normally one
                registered with a connect if you actually want something to
                occur).

            named
                Named arguments which will be passed to receivers. These
                arguments must be a subset of the argument names defined in
                providing_args.

        Return a list of tuple pairs [(receiver, response), ... ]. May raise
        DispatcherKeyError.

        If any receiver raises an error (specifically any subclass of
        Exception), the error instance is returned as the result for that
        receiver.
        """
        if not self.receiver:
            return None, None

        _, weak_receiver = self.receiver
        receiver = weak_receiver()
        try:
            response = receiver(link=self, sender=sender, **named)
        except Exception as err:
            return receiver, err
        else:
            return receiver, response

    def _remove_receiver(self, receiver):
        """
        Remove dead receivers from connections.
        """

        with self.lock:
            self.receiver = None


def receiver(link, **kwargs):
    """
    A decorator for connecting receivers to links. Used by passing in the
    link (or list of links) and keyword arguments to connect::

        @receiver(post_save, sender=MyModel)
        def link_receiver(sender, **kwargs):
            ...

        @receiver([post_save, post_delete], sender=MyModel)
        def links_receiver(sender, **kwargs):
            ...

    """
    def _decorator(func):
        if isinstance(link, (list, tuple)):
            for s in link:
                s.connect(func, **kwargs)
        else:
            link.connect(func, **kwargs)
        return func
    return _decorator


class NamedLink(Link):
    """A named generic notification emitter."""

    def __init__(self, name, *args, **kwargs):
        Link.__init__(self, *args, **kwargs)

        #: The name of this link.
        self.name = name

    def __repr__(self):
        base = Link.__repr__(self)
        return "%s; %r>" % (base[:-1], self.name)


class Namespace(weakref.WeakValueDictionary):
    """A mapping of link names to links."""

    def link(self, name, *args, **kwargs):
        """Return the :class:`NamedLink` *name*, creating it if required.

        Repeated calls to this function will return the same link object.

        """
        try:
            return self[name]
        except KeyError:
            return self.setdefault(name, NamedLink(name, *args, **kwargs))
