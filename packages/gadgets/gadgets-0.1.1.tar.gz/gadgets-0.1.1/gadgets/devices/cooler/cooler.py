from gadgets.devices.device import Device
from gadgets.devices.heater.triggers.temperature import TemperatureTrigger
from gadgets.devices.heater.triggers.temperature import TemperatureTriggerFactory


class Cooler(Device):
    """
    Use this device to cool something down.
    """

    _units = ['celcius', 'C', 'fahrenheit', 'F']
    _on_template = 'cool {location}'
    _off_template = 'stop cooling {location}'

    def __init__(self, location, name, addresses, io_factory=None, trigger_factory=None, on=None, off=None):
        super(Cooler, self).__init__(location, name, addresses, io_factory, trigger_factory, on, off)
        self._target_temperature = None
        comparitor = lambda x, y: x <= y
        self._trigger_factory = TemperatureTriggerFactory(location, addresses, comparitor=comparitor)

    @property
    def events(self):
        return super(Cooler, self).events + ['update temperature']

