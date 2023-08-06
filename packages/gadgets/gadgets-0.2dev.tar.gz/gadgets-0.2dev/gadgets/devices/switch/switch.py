from gadgets.devices.switch.triggers.gpio_timer import GPIOTimer
from gadgets.devices.device import Device
        
class Switch(Device):
    """
    A Switch is used to control items that just need to
    be turned on and off.  Here is an example:
    

    >>> from gadgets.pins.beaglebone import pins
    >>> from gadgets import get_gadgets
    >>> arguments = {
    ...     "locations": {
    ...         "living room": {
    ...             "light": {
    ...             "type": "switch",
    ...             "pin": pins["gpio"][8][3]
    ...             },
    ...         "back yard": {
    ...             "sprinklers": {
    ...             "type": "switch",
    ...             "pin": pins["gpio"][8][11],
    ...             },
    ...         },
    ...     },
    ... }
    >>> gadgets = get_gadgets(arguments)
    >>> gadgets.start()

    Now you can turn it on by creating a socket and giving the switches
    a RCL command::

    >>> from gadgets import Sockets
    >>> s = Sockets()
    >>> s.send("turn on living room light")

    To turn on the sprinklers in the back yard for 15 minutes, you would send
    this command:

    >>> s.send("turn on back yard sprinklers for 15 minutes")
    """

    _trigger_factory = GPIOTimer

    _units = ['minutes', 'minute', 'seconds', 'second', 'hours', 'hour']

    def _get_trigger(self, message):
        return self._trigger_factory(self._location, self._on_event, self._off_event, message, self._addresses, target=self.off)

        
