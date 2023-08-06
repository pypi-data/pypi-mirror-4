import threading, uuid, datetime, time, zmq

from gadgets.devices.trigger import Trigger
from gadgets import Sockets
from gadgets.devices.valve.triggers.volume_converter import VolumeConverter


class GravityTriggerFactory(object):

    def __init__(self, location, addresses, source, tank_radius, valve_radius, valve_coefficient):
        """
        location:          the location in the gadgets system (room, backyard, fish tank, etc.)
        addresses:    the gadgets.Options object for the system
        source:            the container that supplies this location
        tank_radius:       radius of the container
        valve_radius:      duh
        valve_coefficient: a number that can be tweaked to get the calculations
                           correct.  try starting with 0.8
        """
        self._location = location
        self._addresses = addresses
        self._source = source
        self._tank_radius = tank_radius
        self._valve_radius = valve_radius
        self._valve_coefficient = valve_coefficient
        

    def __call__(self, on_event, off_event, message, target):
        uid = str(uuid.uuid1())
        target_volume = message.get('value')
        sockets = Sockets(self._addresses, events=[str(uid)])
        sockets.send('status', {'id': uid})
        returned_uid, message = sockets.recv()
        source_volume = message['locations'][self._source].get('input', {}).get('volume', {}).get('value', 0.0)
        starting_volume = message['locations'][self._location].get('input', {}).get('volume', {}).get('value', 0.0)
        volume_converter = VolumeConverter(
            tank_radius=self._tank_radius,
            valve_radius=self._valve_radius,
            coefficient=self._valve_coefficient
        )
        volume_args = dict(
            source=self._source,
            target_volume=target_volume,
            starting_volume=starting_volume,
            source_volume=source_volume,
            volume_converter=volume_converter
            )
        
        return GravityTrigger(
            self._location,
            on_event,
            off_event,
            message,
            self._addresses,
            target,
            volume_args
        )

class Updater(threading.Thread):

    def __init__(self, start_time, update):
        self._start_time = start_time
        self._update = update
        self._stop_event = threading.Event()
        super(Updater, self).__init__()

    def run(self):
        while not self._stop_event.is_set():
            time_difference = datetime.datetime.now() - self._start_time
            self._update(time_difference.total_seconds())
            time.sleep(1)

    def stop(self):
        self._stop_event.set()

class GravityTrigger(Trigger):

    def __init__(self, location, on_event, off_event, message, addresses, target, volume_args):
        """
        
        """
        self._location = location
        self._target_volume = volume_args['target_volume']
        self._starting_volume = volume_args['starting_volume']
        self._source_volume = volume_args['source_volume']
        self._source = volume_args['source']
        self._volume_converter = volume_args['volume_converter']
        self._invalidated = False
        self._updater = None
        super(GravityTrigger, self).__init__(location, on_event, off_event, message, addresses, target=target)

    def wait(self):
        self._start_time = datetime.datetime.now()
        if self._target_volume is None:
            self._wait_for_stop_event()
        else:
            self._wait_for_time()

    def _wait_for_stop_event(self):
        poller = zmq.Poller()
        poller.register(self.sockets.subscriber, zmq.POLLIN)
        run = True
        while run:
            socks = dict(poller.poll(1000))
            now = datetime.datetime.now()
            if self.sockets.subscriber in socks and socks[self.sockets.subscriber] == zmq.POLLIN:
                event, message = self.sockets.recv()
                if event == self._off_event:
                    run = False
            time_difference = now - self._start_time
            self._update(time_difference.total_seconds())

    def _wait_for_time(self):
        volume = self._target_volume - self._starting_volume
        if volume <= 0:
            self._final_volume = self._starting_volume
            self._final_source_volume = self._source_volume
        else:
            drain_time = self._volume_converter.get_drain_time(self._source_volume, volume)
            self._updater = Updater(self._start_time, self._update)
            self._updater.start()
            time.sleep(drain_time)
            self._updater.stop()
            if not self._invalidated:
                self._final_volume = self._target_volume
                self._final_source_volume = self._source_volume - volume
            else:
                self._final_volume = None
                self._final_source_volume = None

    def _update(self, difference):
        volume = self._volume_converter.get_volume(self._source_volume, difference)
        source_volume = self._source_volume - volume
        total_volume = self._starting_volume + volume
        msg = self._get_message(total_volume, source_volume)
        self.sockets.send('update', msg)

    def _get_message(self, my_volume, source_volume):
        return {
            self._location: {
                'input': {
                    'volume': {
                        'value': my_volume,
                        'units': 'liters'
                    }
                }
            },
            self._source: {
                'input': {
                    'volume': {
                        'value': source_volume,
                        'units': 'liters'
                    }
                }
            }
        }

    def invalidate(self):
        if self._updater is not None:
            self._updater.stop()

    @property
    def status_message(self):
        if self._final_volume is not None:
            msg = self._get_message(self._final_volume, self._final_source_volume)
        else:
            msg = None
        return msg
