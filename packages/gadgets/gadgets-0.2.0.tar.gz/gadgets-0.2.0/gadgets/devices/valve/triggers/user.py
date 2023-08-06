import time, uuid
from gadgets.devices.trigger import Trigger
from gadgets.devices.valve.triggers import TimerTriggerFactory, TimerTrigger
from gadgets import Sockets

class UserTriggerFactory(TimerTriggerFactory):

    def __call__(self, on_event, off_event, message, target):
        uid = str(uuid.uuid1())
        sockets = Sockets(self._addresses, events=[uid])
        sockets.send('status', {'id': uid})
        returned_uid, message = sockets.recv()
        source_volume = message['locations'][self._source].get('input', {}).get('volume', {}).get('value', 0.0)
        volume = message['locations'][self._location].get('input', {}).get('volume', {}).get('value', 0.0)
        sockets.close()
        return UserTrigger(
            self._location,
            on_event,
            off_event,
            message,
            self._addresses,
            target,
            volume,
            self._source,
            source_volume,
        )
        

class UserTrigger(TimerTrigger):

    def __init__(self, location, on_event, off_event, message, addresses, target, volume, source, source_volume, drain_time=None):
        super(UserTrigger, self).__init__(location, on_event, off_event, message, addresses, target, volume, source, source_volume, drain_time=None)
        self._confirmed_event = 'confirmed {0}'.format(on_event)
        self._events = [self._confirmed_event]

    def wait(self):
        event, message = self.sockets.recv()
        if event != self._confirmed_event:
            self.wait()


