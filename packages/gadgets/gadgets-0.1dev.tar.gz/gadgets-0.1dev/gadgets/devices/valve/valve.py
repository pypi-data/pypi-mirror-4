from gadgets.devices.device import Device
from gadgets.errors import GadgetsError

class Valve(Device):

    _units = ['liters', 'gallons']

    def _get_trigger(self, message):
        try:
            trigger = self._trigger_factory(
                self._on_event,
                self._off_event,
                message,
                self.off
            )
        except GadgetsError, e:
            self.off()
        else:
            return trigger

    def _should_get_trigger(self, message):
        return True #we don't want tanks overflowing

    def get_on_event(self):
        return 'fill {0}'.format(self._location)

    def get_off_event(self):
        return 'stop filling {0}'.format(self._location)

    def _register(self):
        super(Valve, self)._register()
        self.sockets.send('update', {self._location: {'volume': {'value': 0.0, 'units': 'liters'}}})

