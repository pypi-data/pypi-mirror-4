from gadgets.devices.trigger import Trigger
from gadgets.io import Poller
from gadgets.errors import GadgetsError

class FloatTriggerFactory(object):

    def __init__(self, location, pin, volume, addresses):
        self._location = location
        self._pin = pin
        self._volume = volume
        self._addresses = addresses

    def __call__(self, on_event, off_event, message, target):
        return FloatTrigger(
            self._location,
            on_event,
            off_event,
            message,
            self._addresses,
            target,
            self._pin,
            self._volume
        )

class FloatTrigger(Trigger):
    """
    Waits until the gpio pin goes high, then calls the given target method.
    """

    _poller_class = Poller #this can be switched by tests
    _direction = 'input'

    def __init__(self, location, on_event, off_event, message, addresses, target, pin, volume):
        self._volume = volume
        self._pin = pin
        super(FloatTrigger, self).__init__(location, on_event, off_event, message, addresses, target=target)

    def wait(self):
        try:
            poller = self._poller_class(self._pin)
        except GadgetsError, e:
            raise GadgetsError(str(e), self.sockets)
        poller.wait()
        poller.close()

    @property
    def status_message(self):
        return {
            self._location: {
                self._direction: {
                    'volume': {
                        'value': self._volume,
                        'units': 'liters'
                    }
                }
            }
        }

        
        