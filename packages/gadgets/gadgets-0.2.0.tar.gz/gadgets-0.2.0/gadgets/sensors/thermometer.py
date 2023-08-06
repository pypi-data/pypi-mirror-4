import time, zmq
import threading
from collections import defaultdict, namedtuple
from gadgets import Gadget

def thermometer_factory(location, name, arguments, addresses):
    
    if thermometer_factory.server is None:
        thermometer_factory.server = ThermometerServer(addresses, timeout=arguments.get('timeout', 5))
        thermometer_factory.server.start()
    return Thermometer(
        location,
        name,
        addresses,
        uid=arguments['uid'],
        timeout=arguments.get('timeout', 5)
    )

thermometer_factory.server = None

class Thermometer(Gadget):
    """
    When you install Ubuntu or Angstom on a Beaglebone you have access
    to a sysfs interface for dallas 1-wire devices.  Connect a DS18B20+
    temperature sensor to the beaglebone like this::

                          +---------+
                          |         |
                          |  front  |
                          |         |
                          |         |
                          |         |
                          +-+--+--+-+
                            |  |  |
                            |  |  |
                            |  |  |
                            |  |  |
                            |  |  |
                            1  2  3

    Where::

        1 = ground (port 9, pin 1 or 2)
        2 = data   (port 8, pin 6)
        3 = Vcc    (port 9, pin 3 or 4)

    Once you have it connected you can read the temperature from the following
    file::

        $ cat /sys/bus/w1/devices/<unique id>/w1_slave
        b8 01 4b 46 7f ff 08 10 8a : crc=8a YES
        b8 01 4b 46 7f ff 08 10 8a t=27500
    
    Where <unique id> is the embedded uid of the sensor.  Thermometer
    parses the w1_slave file and reports the temperature to the gadgets system.

    To use Thermometer give it a dictionary that maps the location of the
    sensor to its unique id:

    >>> from gadgets import get_gadgets
    >>> from gadgets.pins.beaglebone import pins
    >>> arguments = {
    ...     'locations': {
    ...         'living room': {
    ...             'thermometer': {
    ...                 'type': 'thermometer',
    ...                 'uid': 'uid': '28-0000025f0aba',
    ...              }
    ...          }
    ...      }
    >>> gadgets = get_gadgets(arguments)
    >>> gadgets.start()

    Now the thermometer will start and report its temperature
    to the gadgets system.
    """

    _read_path = '/sys/bus/w1/devices/{0}/w1_slave'
    _direction = 'input'
    

    @property
    def events(self):
        return []

    def __init__(self, location, name, addresses, uid, timeout=5):
        
        self._uid = uid
        self.value = 0.0
        self._buf = None
        super(Thermometer, self).__init__(location, name, addresses, timeout=timeout)

    @property
    def buf(self):
        if self._buf is None:
            self._buf = open(self._read_path.format(self._uid, 'r'))
        return self._buf

    def _get_value(self):
        s = self.buf.read()
        i = s.find('t=')
        self.buf.seek(0)
        return float(s[i+2:]) / 1000.0

    def event_received(self, event, message):
        "event recieved is triggered because of the timeout"
        try:
            value = self._get_value()
        except ValueError:
            pass
        else:
            difference = abs(self.value - value)
            if value is not None and value >= 0 and difference > 0: #sometimes the dallas thermometers seem to crap out and show an invalid negative value
                self.sockets.send('thermometer server', {'value': value, 'location': self._location})
            self.value = value

    def _register(self):
        self.sockets.send(
            'register',
            {
                'location': self._location,
                'direction': self._direction,
                'name': self._name,
                'uid': self.uid,
                'value': self._get_value()
            }
        )
        
    
    def do_shutdown(self):
        self.buf.close()

class ThermometerServer(Gadget):

    """
    ThermometerServer is intended as a way to consolidate
    the temperature readings and send them all at once
    to the Coordinator.
    """
    _direction = 'input'

    def __init__(self, addresses, timeout=5):
        self._values = defaultdict(dict)
        super(ThermometerServer, self).__init__('null', 'thermometer', addresses, timeout=timeout)

    @property
    def events(self):
        return ['thermometer server']

    def event_received(self, event, message):
        if event is None: #a poller timeout
            self.sockets.send('update temperature', self._values)
        else:
            msg = {'value': message['value'], 'units': 'C'}
            try:
                self._values[message['location']][self._direction]['temperature'] = msg
            except KeyError:
                self._values[message['location']] = defaultdict(dict)
                self._values[message['location']][self._direction]['temperature'] = msg

    def _register(self):
        pass
                                   

