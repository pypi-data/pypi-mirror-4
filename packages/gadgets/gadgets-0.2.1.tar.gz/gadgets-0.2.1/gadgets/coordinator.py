import time, threading
from collections import defaultdict

from gadgets.sockets import Sockets
from gadgets.errors import GadgetsError
from gadgets.rcl import MethodRunner


class Coordinator(threading.Thread):
    """
    The Coordinator keeps track of the state of all the gadgets
    and provides a few ways for gadgets to request information.
    Coordinator listens for the following events (this defines
    the zmq-based API for gadgets):

    register: When a gadget starts up it sends a register message.
              The register message just lets the Coordinator know
              that there is a new Gadget.  If the Gadget is a Device
              then the register message also includes the commands
              that turn the device on and off.

        >>> sockets.send('register', {
                'location': '<some location>',
                'name': '<some name>',
                'on': '<some on event>',
                'off': '<some off event>',    
            })
    
    method:  A method is a list of RCL messages.  If Coordinator
             receives a method message it starts up an instance
             of MethodRunner which then executes the method.

        >>> sockets.send('method', {
                'method': [
                    'turn on living room light',
                    'wait for 1 hour',
                    'turn off living room light'
                ]
            })

    update:  Whenever a Gadget reaches some new state, it should
             send an update message.  The Coordinator reads the message
             and updates its _state attribute.  The _state attribute
             is accessible to the outside world via the status message
             (see status below).  After Coordinator receives an update
             event, it sends an UPDATE event that contains the _state
             dict.  The UPDATE event is intended for GUIs.  Whenever
             something changes a GUI would want to be immediately
             notified.

         >>> sockets.send('update', {
                 '<some location>': {
                     '<some name>': {
                         'value': True
                    }
                }
            })

    status:  Send a status message and the response is the _state dict
             of the Coordinator.  Do with that state what you will.  The
             message should contain the id of the entity that sent the
             request.

        >>> sockets.send('status', {
                'id': '<some unique id>'
            })
        >>> _id, status = sockets.recv()

    events:  This message is also a request.  The response is all the
             on and off events that the Coordinator knows of due to
             gadgets registering and including 'on' and 'off' in the
             register message (see register above).  This is useful
             for GUIs to be able to know how to turn things on and
             off.

        >>> sockets.send('events', {
                'id': '<some unique id>'
            })
        >>> _id, events = sockets.recv()

    locations:  Another request that is useful for GUIs.  The response
                is a list of all the locations in the system that are
                registered with the Coordinator.

        >>> sockets.send('locations', {
                'id': '<some unique id>'
            })
        >>> _id, locations = sockets.recv()

    shutdown:  If this message is sent than all Gadget subclasses
               and the Coordinator will exit their main loops and
               die.  This message shuts down the whole system.

        >>> sockets.send('shutdown')

    error:  Any gadget can send this message and it will be stored
            in the _state attribute of the Coordinator.

        >>> sockets.send('error', {
                'error': '<some error message>'
                'id': '<some unique id>'
            })
    """

    def __init__(self, addresses):
        self._addresses = addresses
        self._ids = []

        self._sockets = None
        self._external_events = defaultdict(dict)
        self._event_handlers = {
            'register': self._handle_register,
            'method': self._run_method,
            'update': self._update,
            'status': self._status,
            'events': self._get_events,
            'locations': self._get_locations,
            'shutdown': self._shutdown,
            'error': self._get_error
            }
        
        self._state = {
            'locations': defaultdict(dict),
            'method': {},
            'errors': []
        }
        super(Coordinator, self).__init__()


    def run(self):
        stop = False
        self.sockets.send('startup')
        while stop != True:
            stop = self._recv()
        self.sockets.close()

    @property
    def _events(self):
        return self._event_handlers.keys()

    @property
    def sockets(self):
        if self._sockets is None:
            self._sockets = Sockets(self._addresses, events=self._events)
        return self._sockets

    def _recv(self):
        event, message = self.sockets.recv()
        return_value = False
        if event in self._event_handlers:
            f = self._event_handlers[event]
            return_value = f(message)
        return return_value

    def _run_method(self, message):
        """
        a method message looks like:
        {'method': [
             'turn on light',
             'wait 10 seconds',
             'turn off light'
             ]
        }
        """
        self._state['method']['method'] = message['method']
        self._method_runner = MethodRunner(message['method'], self._addresses)
        self._method_runner.start()

    def _update_method(self, message):
        if 'step' in message['method']:
            self._state['method']['step'] = message['method']['step']
        elif 'complete' in message['method']:
            self._method_runner = None
            self._state['method'] = {}
        elif 'countdown' in message['method']:
            self._state['method']['countdown'] = message['method']['countdown']

    def _update_location(self, message):
        for location in message:
            for direction in message[location]:
                for name, val in message[location][direction].iteritems():
                    value = val['value']
                    units = val.get('units')
                    self._do_update(location, name, direction, value, units)

    def _update(self, message):
        """
        save the value in the message and pass it along to
        all the gadgets that care.
        
        To update, a gadget must send a message that looks
        like:

                  LOCATION    DIRECTION      NAME        
        update {'livingroom': {'input': {'temperature': {'value': 33, 'units': 'C'}}}}
        """
        if 'method' in message:
            self._update_method(message)
        else:
            self._update_location(message)
        self.sockets.send('UPDATE', self._state)

    def _do_update(self, location, name, direction, value, units):
        if direction not in self._state['locations'][location]:
            self._state['locations'][location][direction] = dict()
        if name not in self._state['locations'][location][direction]:
            self._state['locations'][location][direction][name] = defaultdict(dict)
        self._state['locations'][location][direction][name]['value'] = value
        self._state['locations'][location][direction][name]['units'] = units
        self._state['sender'] = '{0} {1}'.format(location, name)
        
    def _is_valid_update_message(self, message):
        return True

    def _register(self, gadget):
        pass

    def _status(self, message):
        _id = message['id']
        self.sockets.send('{0} status'.format(str(_id)), self._state)

    def _handle_register(self, message):
        """
        When a gadget starts up, it must register with the
        system.  Sensors do not have to register.  A register
        message looks like:

        register {
            'location': 'livingroom',
            'name': 'heater',
            'on': 'heat livingroom',
            'off': 'stop heating livingroom'
        }

        An id is assigned and a response is sent with a
        topic and message that looks like:

        livingroom heater registration {'id': 3}
        """
        if self._is_valid_registration_message(message):
            uid = message['uid']
            if uid not in self._ids:
                location = message['location']
                name = message['name']
                direction = message['direction']
                value = message.get('value')
                if direction not in self._state['locations'][location]:
                    self._state['locations'][location] = {'input': {}, 'output': {}}
                self._state['locations'][location][direction][name] = {
                    'id': uid,
                    'value': value,
                }
                if message.get('on') and message.get('off'):
                    self._external_events[location][name] = {
                        'on': message['on'],
                        'off': message['off'],
                    }
                if message.get('input'):
                    self._state['locations'][location][direction][name]['input'] = True
                self._ids.append(uid)
                
    def _is_valid_registration_message(self, message):
        return True
        #return set(message.keys()) == {'name', 'location', 'on', 'off', 'uid'}

    def _get_events(self, message):
        _id = message['id']
        self.sockets.send('{0} events'.format(str(_id)), self._external_events)

    def _get_locations(self, message):
        _id = message['id']
        self.sockets.send(str(_id), self._state['locations'].keys())

    def _shutdown(self, message):
        return True

    def _get_error(self, message):
        self._state['errors'].append(message.get('error'))
