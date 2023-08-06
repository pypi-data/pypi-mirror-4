import threading, time, zmq
from gadgets.sockets import Sockets


class Gadget(threading.Thread):
    """
    The components that run in the gadgets system should be a subclass
    of Gadget.  

    After a gadget starts and registers, it listens for zmq messages
    that are specified by the events attribute.  (see the gadgets.sockets
    module for more details).  After a message is received the 'event_received'
    method is called.
    
    There are many possible uses of Gadget subclasses.  One of the main
    subclasses built into Gadgets is Device.  It is meant for controlling
    physical devices.  A Gadget subclass isn't just for interfacing with
    hardware.  For example, here is a class that records all of the goings
    on of the system::

    >>> class Recorder(Gadget):
    ...     @property
    ...        def events(self):   
    ...            return ['UPDATE']
    ...
    ...     def event_received(self, event, message):
    ...         with open('/tmp/gadgets_data.txt', 'a') as buf:
    ...             buf.write(json.dumps(message))

    It would probably better to make one that saves the messages to
    a database.
    
    In order to make a Gadgets subclass, you must define an events
    property and implement event_received.  The event_received
    will only receive messages that you specified in the events
    property.
    """

    def __init__(self, location, name, addresses, timeout=None):
        self._timeout = timeout
        self._addresses = addresses
        self._location = location
        self._name = name
        self._id = '{0} {1}'.format(self._location, self._name)
        self._registration_event = '{0} registration'.format(self._id)
        self._sockets = None
        self._events_cache = None
        super(Gadget, self).__init__()

    @property
    def uid(self):
        """
        A gadget uid us composed of the location and name
        properties.  No two Gadget instances should have
        the same uid.
        """
        return '{0} {1}'.format(self._location, self._name)

    @property
    def events(self):
        """
        Returns a list of events that will trigger the event_received method
        """
        raise NotImplemented()

    def event_received(self, event, message):
        """
        receives the events defined by self.events
        """
        raise NotImplemented()

    def do_shutdown(self):
        """
        override this if your subclass needs to do more stuff
        in order to shutdown cleanly.
        """
        pass

    def run(self):
        self._register()
        self._stop = False
        if self._timeout is not None:
            poller = zmq.Poller()
            poller.register(self.sockets.subscriber, zmq.POLLIN)
        while not self._stop:
            if self._timeout:
                socks = dict(poller.poll(timeout=self._timeout * 1000))
                if self.sockets.subscriber in socks and socks[self.sockets.subscriber] == zmq.POLLIN:
                    event, message = self.sockets.recv()
                else:
                    event, message = None, None
            else:
                event, message = self.sockets.recv()
            self._do_event_received(event, message)
        self.sockets.close()
        self.do_shutdown()

    def _do_event_received(self, event, message):
        if event == 'status':
            self.sockets.send(str(message['id']), self.status)
        elif event == 'shutdown':
            self._stop = True
        else:
            self.event_received(event, message)

    @property
    def status(self):
        """Device overrides this property to indicate weather or not
        the Device is turned on"""
        return False

    @property
    def _events(self):
        if self._events_cache is None:
            self._events_cache = ['status', 'shutdown', self._id, self._registration_event] + self.events
        return self._events_cache

    @property
    def sockets(self):
        if self._sockets is None:
            self._sockets = Sockets(self._addresses, events=self._events)
        return self._sockets

    def _register(self):
        self.sockets.send(
            'register',
            {
                'location': self._location,
                'name': self._name,
                'uid': self.uid,
                'direction': self._direction
            }
        )
        
