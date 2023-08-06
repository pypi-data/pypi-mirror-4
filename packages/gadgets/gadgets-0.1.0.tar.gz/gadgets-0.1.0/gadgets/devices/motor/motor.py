import time
from gadgets.devices.device import Device

class Motor(Device):
    """
    Motor is a general class for controlling a motor.  It should be
    able to control any motor, as long as it is initialized with
    an io object that can interface with the physical interface
    that is being used.
    

    >>> from gadgets import get_gadgets
    >>> from gadgets.pins.beaglebone import pins
    >>> brewery_def = {
    ...     'locations': {
    ...         'front yard': {
    ...             'camera': {
    ...                 'type': 'motor',
    ...                 'gpio_a': 'gpio_a': pins['gpio'][8][24],
    ...                 'gpio_b': pins['gpio'][8][25],
    ...                 'pwm': pins['pwm'][8][13],
    ...                 'poller': pins['gpio'][8][27]
    ...            }
    ...         }
    ...     }
    ... }

    If the motor you are controlling comes with an encoder (the example
    above assumes an encoder) then you can turn it on with a RCL
    command that uses 'ticks' as its units::

    >>> from gadgets import Sockets
    >>> sock = Sockets()
    >>> sock.send('turn on top motor for 40 ticks')
    
    """

    _time_units= ('hours', 'minutes', 'seconds', 'hour', 'minute', 'second')
    _percent_units = ('percent',)
    _counter_units = ('ticks',)
    _units = _time_units + _percent_units + _counter_units

    def _should_get_trigger(self, message):
        units = message.get('units')
        return units in self._time_units or units in self._counter_units

    def on(self, message):
        """
        value should range from -100 to 100 for full power counter-
        clockwise to full power clockwise.
        """
        if self._should_get_trigger(message):
            self._invalidate_trigger()
            self._off_trigger = self._get_trigger(message)
            self._off_trigger.start()
        units = message.get('units')
        if units == 'ticks':
            ticks = message['value']
            if ticks < 0:
                value = -100
            else:
                value = 100
            time.sleep(0.1)
            self.io.on({'value': value, 'units': 'percent'})
        else:
            self.io.on(message)
        self._update_status(True)

    def off(self, message):
        """
        value should range from -100 to 100 for full power counter-
        clockwise to full power clockwise.
        """
        self.io.off()
        self._update_status(False)
        
    