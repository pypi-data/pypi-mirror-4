import zmq, json, time
import threading

from zmq.devices import ThreadDevice


class Addresses(object):
    """
    Addresses is a helper class that lets Broker and Sockets easily
    connect to the correct url and port.

    A Gadgets system can be distributed across multiple computers.
    You must decide which instance is the master, and use the default
    'localhost' as the host name.  The subsequent instances can then
    be given the ip address of the master system.  Then all Gadgets
    instances will be able to communicate with each other.
    """

    def __init__(self, host='localhost', in_port=6111, out_port=6112):
        """
        host: the host name of the master gadgets instance
              (the one that is running with localhost as the
              host name)
        in_port: the port number that Socket uses for its
                 subscriber socket
        out_port: the port number that Socket uses for its
                  publisher socket
        """
        self.out_address = 'tcp://{0}:{1}'.format(host, out_port)
        self.in_bind_address = 'tcp://*:{0}'.format(out_port)
        self.in_address = 'tcp://{0}:{1}'.format(host, in_port)
        self.out_bind_address = 'tcp://*:{0}'.format(in_port)

        
class Broker(threading.Thread):
    """
    This is used internally by each Gadgets instance.  You
    shouldn't need to use this class.
    """
    
    def __init__(self, addresses=None):
        """
        addresses: an instance of gadgets.address:Address
        """
        if addresses is None:
            self._addresses = Addresses()
        else:
            self._addresses = addresses
        super(Broker, self).__init__()

    def run(self):
        context = zmq.Context.instance()
        subscriber = context.socket(zmq.SUB)
        subscriber.setsockopt(zmq.SUBSCRIBE, '')
        subscriber.bind(self._addresses.in_bind_address)
        publisher = context.socket(zmq.PUB)
        publisher.bind(self._addresses.out_bind_address)
        run = True
        time.sleep(0.2)
        while run:
            parts = subscriber.recv_multipart()
            if parts[0] ==  'shutdown':
                run = False
            if len(parts) != 2 or parts[1] == 'true' or parts[1] == 'false': #why am I getting these, no one sends them
                continue
            publisher.send_multipart(parts)
        time.sleep(1)
        subscriber.close()
        publisher.close()

        
class Sockets(object):
    """
    Every subclass of Gadget uses this class for all of 
    its communication.  You can also use this class if
    you wish to communicate with the system without 
    a Gadget subclass (on the command line for example).

    Sockets wraps two zeromq sockets and uses them to
    receive incoming messages and send messages out to
    the rest of the system.  It uses zmq.SUB and zmq.PUB
    so each Gadget can control which incoming events
    it receives.  The events argument in __init__ determines
    what events will be received.
    """
    
    def __init__(self, addresses=None, events=[]):
        """
        addresses: an instance of gadgets.address:Address
        events: a list of events to subscribe to.  Only 
                messages that start with the events in
                this list will be received.

                NOTE: If you subscribe to 'update'
                      you will receive messages like
                      'update temperature'
        """
        self.context = zmq.Context.instance()
        if addresses is None:
            addresses = Addresses()
        self.subscriber = self.context.socket(zmq.SUB)
        self.subscriber.connect(addresses.in_address)
        for event in events:
            self.subscriber.setsockopt(zmq.SUBSCRIBE, event)
        self.publisher = self.context.socket(zmq.PUB)
        self.publisher.connect(addresses.out_address)
        time.sleep(0.2)
        
    def send(self, event, message={}):
        """
        The first argument, event, determines what sockets will receive
        the message.  The message argument is any JSON serializable object.
        For example:

        >>> from gadgets import Sockets
        >>> sock = Sockets()
        >>> sock.send('howdy', ['abc'])
        """
        self.publisher.send_multipart([event, json.dumps(message, ensure_ascii=True)])

    def recv(self):
        """
        If a Sockets object that was initialized like this:

        >>> from gadgets import Sockets
        >>> sock = Sockets(events=['howdy'])
        
        sock.recv() will block until some other Sockets instance sends
        a message with 'howdy' as the event.

        >>> event, message = sock.recv()
        >>> print event
        howdy
        """
        parts = self.subscriber.recv_multipart()
        if len(parts) != 2:
            raise Exception(str(parts))
        event, message = parts
        return event, json.loads(message)
        
    def close(self):
        self.publisher.close()
        self.subscriber.close()

