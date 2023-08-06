from gadgets.devices.switch.triggers.gpio_timer import GPIOTimer
from gadgets.devices.device import Device
        
class Switch(Device):
    """
    See README.md from the root of the gadgets package for
    details on how to use Switch.
    """

    _trigger_factory = GPIOTimer

    _units = ['minutes', 'minute', 'seconds', 'second', 'hours', 'hour']

    def _get_trigger(self, message):
        return self._trigger_factory(self._location, self._on_event, self._off_event, message, self._addresses, target=self.off)

        
