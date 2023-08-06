from gadgets.io.io import IO
from gadgets import Sockets


class ShiftRegisterIOFactory(object):
    
    def __init__(self, addresses, channel):
        self._addresses = addresses
        self._channel = channel
    
    def __call__(self):
        return ShiftRegisterIO(self._addresses, self._channel)


class ShiftRegisterIO(IO):

    """
    Implements the gadgets io api (on, off, close, and status)
    see gadgets.io.io.

    A Beaglebone has lots of gpio pins available, so why use a
    power logic shift register (such as a TPIC6B595)?  The gpio
    pins cannot provide enough current to power much more than
    a transistor.  So if you want to turn on a sollid state
    relay or a solenoid then you need to use a transistror
    or mosfet.  The use of the shift register elminates the
    need for transistors in many cases.  Also, you can chain
    multiple shift registers together and get many more gpio
    pins than you could get with a single beaglebone:
    
    >>> from gadgets import get_gadgets
    >>> arguments = {
    ...     "locations": {
    ...         "back yard": {
    ...             "sprinklers": {
    ...                 "type": "shift register switch",
    ...                 "channel": 3,
    ...                 "on": "water {location}",
    ...                 "off": "stop watering {location}"
    ...            }
    ...         }
    ...     }
    ... }
    >>> gadgets = get_gadgets(arguments)

    Note that you can pass in an 'on' and 'off' argument for
    a device.  This allows you to turn the device on with a
    command other than the default.  The default on and off
    commands in this case would have been 'turn on back yard
    sprinklers' and 'turn off back yard sprinklers'.  Now in
    another terminal:

    >>> from gadgets import Sockets
    >>> sock = Sockets()
    >>> sock.send('water back yard for 10 minutes')
    """

    def __init__(self, addresses, channel):
        self._sockets = Sockets(addresses)
        self._channel = channel
        self._status = False

    @property
    def status(self):
        return self._status
        
    def on(self):
        self._send(True)

    def off(self):
        self._send(False)

    def close(self):
        self._sockets.close()

    @property
    def value(self):
        return self.status

    def _send(self, value):
        self._sockets.send(
            'shift register server',
            {'value': value, 'channel': self._channel}
        )
        self._status = value
