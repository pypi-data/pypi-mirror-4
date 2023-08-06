import time
from gadgets.devices.device import Device

class Motor(Device):

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
        
    