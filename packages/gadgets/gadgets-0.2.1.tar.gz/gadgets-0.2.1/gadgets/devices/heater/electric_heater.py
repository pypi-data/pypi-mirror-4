from gadgets.devices.device import Device
from gadgets.devices.heater.triggers.temperature import TemperatureTriggerFactory

class ElectricHeater(Device):
    """
    Used to control electric heating coils on my brewery.  Here
    is an example of its use:

    >>> from gadgets import get_gadgets
    >>> from gadgets.pins.beaglebone import pins
    >>> brewery_def = {
    ...     'locations': {
    ...         'boiler': {
    ...             'heater': {
    ...                 'type': 'electric heater',
    ...                 'pin': pins['pwm'][8][13],
    ...             }
    ...         }
    ...     }
    ... }
    >>> brewery = get_gadgets(brewery_def)
    >>> brewery.start()
    
    If you turn on the electric heater with a target temperature
    like this:

    >>> from gadgets import Sockets
    >>> sock = Sockets()
    >>> sock.send('heat boiler 180 F')
    
    then as the temperature of the pot approaches the target temperature
    it will use its pwm pin to apply less heat to the pot so the heater
    won't over heat the container.
    """

    _units = ['celcius', 'C', 'fahrenheit', 'F']
    _on_template = 'heat {location}'
    _off_template = 'stop heating {location}'

    def __init__(self, location, name, addresses, io_factory=None, trigger_factory=None, on=None, off=None):
        super(ElectricHeater, self).__init__(location, name, addresses, io_factory, trigger_factory, on, off)
        self._target_temperature = None
        self._trigger_factory = TemperatureTriggerFactory(location, addresses)

    @property
    def events(self):
        return super(ElectricHeater, self).events + ['update temperature']

    def _get_trigger(self, message):
        return self._trigger_factory(self._on_event, self._off_event, message, target=None)

    def event_received(self, event, message):
        print 'e r', event, message
        if event.startswith('update temperature'):
            self._update_pwm(message)
        else:
            super(ElectricHeater, self).event_received(event, message)

    def on(self, message):
        print 'elec on'
        self._target_temperature = self._get_temperature(message)
        super(ElectricHeater, self).on(message)

    def off(self, message=None):
        self._target_temperature = None
        super(ElectricHeater, self).off(message)

    def _get_temperature(self, message):
        if message.get('units') in self._units:
            units = message['units']
            value = message['value']
            if units == 'F' or units == 'fahrenheit':
                value = (value * 1.8) + 32.0
            return value

    @property
    def io(self):
        if self._io is None:
            self._io = self._io_factory()
            self._io.start()
        return self._io

    def _update_pwm(self, message):
        if not self.io.status:
            return
        if self._location in message:
            temperature = self._get_temperature(message[self._location]['input']['temperature'])
            self.io.duty_percent = self._get_duty_percent(temperature)

    def _get_duty_percent(self, temperature):
        if self._target_temperature is None:
            duty_percent = 100
        else:
            difference = self._target_temperature - temperature
            if difference is None or difference <= 0:
                duty_percent = 0
            elif difference <= 1:
                duty_percent = 25
            elif difference <= 2:
                duty_percent = 50
            else:
                duty_percent = 100
        return duty_percent


        
        
