from gadgets.devices.device import Device
from gadgets.devices.heater.triggers.temperature import TemperatureTriggerFactory

class ElectricHeater(Device):

    _units = ['celcius', 'C', 'fahrenheit', 'F']

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
        if event.startswith('update temperature'):
            self._update_pwm(message)
        else:
            super(ElectricHeater, self).event_received(event, message)

    def on(self, message):
        self._target_temperature = self._get_temperature(message)
        super(ElectricHeater, self).on(message)

    def off(self, message=None):
        self._target_temperature = None
        super(ElectricHeater, self).off(message)

    def get_on_event(self):
        return 'heat {0}'.format(self._location)

    def get_off_event(self):
        return 'stop heating {0}'.format(self._location)

    def _get_temperature(self, message):
        if message.get('units') in self._units:
            units = message['units']
            value = message['value']
            if units == 'F' or units == 'fahrenheit':
                value = (value * 1.8) + 32.0
            return value

    def _update_pwm(self, message):
        if not self.io.status:
            return
        if self._location in message:
            temperature = self._get_temperature(message[self._location]['temperature'])
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


        
        
