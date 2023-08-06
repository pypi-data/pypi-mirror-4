import time, uuid
from gadgets.devices.trigger import Trigger
from gadgets import Sockets

class TimerTriggerFactory(object):

    def __init__(self, location, addresses, source, drain_time=None):
        self._location = location
        self._source = source
        if drain_time is not None:
            self._drain_time = drain_time * 60
        else:
            self._drain_time = None
        self._addresses = addresses

    def __call__(self, on_event, off_event, message, target):
        uid = str(uuid.uuid1())
        sockets = Sockets(self._addresses, events=[uid])
        sockets.send('status', {'id': uid})
        returned_uid, message = sockets.recv()
        source_volume = message['locations'][self._source].get('input', {}).get('volume', {}).get('value', 0.0)
        volume = message['locations'][self._location].get('input', {}).get('volume', {}).get('value', 0.0)
        sockets.close()
        return TimerTrigger(
            self._location,
            on_event,
            off_event,
            message,
            self._addresses,
            target,
            volume,
            self._source,
            source_volume,
            self._drain_time
        )

class TimerTrigger(Trigger):

    _direction = 'input'

    def __init__(self, location, on_event, off_event, message, addresses, target, volume, source, source_volume, drain_time=None):
        self._source = source
        self._source_volume = source_volume
        self._volume = volume
        self._drain_time = drain_time
        self._invalidated = False
        super(TimerTrigger, self).__init__(location, on_event, off_event, message, addresses, target=target)

    def wait(self):
        time.sleep(self._drain_time)

    def invalidate(self):
        self._invalidated = True

    @property
    def status_message(self):
        if not self._invalidated:
            msg = {
                self._location: {
                    self._direction: {
                        'volume': {
                            'value': self._source_volume + self._volume,
                            'units': 'liters'
                        }
                    }
                },
                self._source: {
                    self._direction: {
                        'volume': {
                            'value': 0,
                            'units': 'liters'
                        }
                    }
                }
            }
            return msg
