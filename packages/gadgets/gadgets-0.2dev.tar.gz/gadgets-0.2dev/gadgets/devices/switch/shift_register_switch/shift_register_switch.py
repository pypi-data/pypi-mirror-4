from gadgets.devices.switch.triggers.gpio_timer import GPIOTimer
from gadgets.devices.device import Device
from gadgets import Sockets

class ShiftRegisterIO(object):

    """
    Implements the gadgets io api (on, off, close, and status)
    """

    def __init__(self, addresses, channel):
        self._sockets = Sockets(addresses)
        self._channel = channel
        self.status = False
        
    def on(self):
        self._send(True)

    def off(self):
        self._send(False)

    def close(self):
        self._sockets.close()

    def _send(self, value):
        self._sockets.send(
            'shift register server',
            {'value': value, 'channel': self._channel}
        )
        self.status = value

class ShiftRegisterIOFactory(object):
    
    def __init__(self, addresses, channel):
        self._addresses = addresses
        self._channel = channel
    
    def __call__(self):
        return ShiftRegisterIO(self._addresses, self._channel)

        
class ShiftRegisterSwitch(Device):
    """
    A Beaglebone has lots of gpio pins available, so why use a
    power logic shift register (such as a TPIC6B595)?  The gpio
    pins cannot provide enough current to power much more than
    a transistor.  So if you want to turn on a sollid state
    relay or a solenoid then you need to use a transistror
    or mosfet.  The use of the shift register elminates the
    need for transistors in many cases:

    
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

    _trigger_factory = GPIOTimer

    _units = ['minutes', 'minute', 'seconds', 'second', 'hours', 'hour']

    def _get_trigger(self, message):
        return self._trigger_factory(
            self._location,
            self._on_event,
            self._off_event,
            message,
            self._addresses,
            target=self.off
        )

    def do_shutdown(self):
        self.io.close()


        
