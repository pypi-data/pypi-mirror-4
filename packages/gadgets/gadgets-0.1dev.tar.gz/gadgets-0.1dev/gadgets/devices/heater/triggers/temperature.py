import uuid
from gadgets.devices.trigger import Trigger

class TemperatureTriggerFactory(object):

    def __init__(self, location, addresses, comparitor=None):
        self._location = location
        self._addresses = addresses
        if comparitor is None:
            self._comparitor = lambda x, y: x >= y
        else:
            self._comparitor = comparitor
        
    def __call__(self, on_event, off_event, message, target=None):
        return TemperatureTrigger(self._location, on_event, off_event, message, self._addresses, self._comparitor, target=target)
        

class TemperatureTrigger(Trigger):

    _units = ['celcius', 'C', 'fahrenheit', 'F']

    def __init__(self, location, on_event, off_event, message, addresses, comparitor, target=None):
        super(TemperatureTrigger, self).__init__(location, on_event, off_event, message, addresses)
        self._events = ['update temperature', 'shutdown']
        self._target = target
        self._target_temperature = self._get_temperature(self._message)
        self._comparitor = comparitor

    def _get_temperature(self, message):
        if message.get('units') in self._units:
            units = message['units']
            value = message['value']
            if units == 'F' or units == 'fahrenheit':
                value = (value * 1.8) + 32.0
            return value

    def _is_mine(self, message):
        return message.get(self._location, {}).get('temperature') is not None

    def _target_reached(self, message):
        if not self._is_mine(message):
            ret = False
        else:
            temperature = self._get_temperature(message[self._location]['temperature'])
            print temperature
            ret = self._comparitor(temperature, self._target_temperature)
            print ret
        return ret
        
    def wait(self):
        event, message = self.sockets.recv()
        if event != 'shutdown' and not self._target_reached(message):
            self.wait()
