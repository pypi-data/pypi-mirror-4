import threading, zmq, time, json, sys, uuid
from gadgets import Addresses, Sockets

class DataGetter(threading.Thread):
    
    def __init__(self, target, addresses):
        self.uid = str(uuid.uuid1())
        self._addresses = addresses
        self._stop_event = threading.Event()
        self.commands = {}
        super(DataGetter, self).__init__()
        self._target = target
        self._sockets = None
        self.locations = None

    def do_shutdown(self):
        self._stop_event.set()

    def run(self):
        self.main_loop()

    def main_loop(self):
        self.sockets.send('status', {'id': self.uid})
        event, status = self.sockets.recv()
        self.locations = status['locations'].keys()
        self.sockets.send('events', {'id': self.uid})
        _id, self.commands = self.sockets.recv()
        self._target(status)
        poller = zmq.Poller()
        poller.register(self.sockets.subscriber, zmq.POLLIN)
        while not self._stop_event.isSet():
            self._get_data(poller)
        self.sockets.close()

    def _get_data(self, poller):
        socks = dict(poller.poll(1000))
        if self.sockets.subscriber in socks and socks[self.sockets.subscriber] == zmq.POLLIN:
            event, msg = self.sockets.recv()
            if not self._target(msg):
                self._stop_event.set()
                return

    def stop(self):
        self._stop_event.set()

    @property
    def sockets(self):
        if self._sockets is None:
            self._sockets = Sockets(self._addresses, events=['UPDATE', self.uid])
        return self._sockets

def print_data(data):
    return True


if __name__ == '__main__':
    host = sys.argv[1]
    addresses = Addresses(host=host)
    dg = DataGetter(print_data, addresses)
    dg.start()

