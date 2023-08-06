import operator
import struct
from gadgets import Gadget
from gadgets.io import GPIO
try:
    from pyctu.commands.api import API
    from pyctu.commands.api_packet import APIPacket
except ImportError:
    API = None
    APIPacket = None

    
class XBeeServer(Gadget):
    """
    The remote XBee modules can be controlled by sending api packets from
    a module that is connected to gadgets system.  A XBeeServer is needed
    because only its serial interface can only be used by one process/thread.
    """

    _XBee_Class = API #this may be switched to something else for testing
    _address_struct = struct.Struct('>Q')
    _direction = 'output'

    def __init__(self, location, name, addresses, device):
        self._device = device
        self._highest_channel = 0
        self._state = 0
        self._xbee = None
        self._shift_registers = None
        super(XBeeServer, self).__init__(location, name, addresses)

    def event_received(self, event, message):
        """
        This is the entry point for each new message.
        """
        channel = message['channel']
        address = self._address_struct.pack(message['address'])
        value = '\x05' if message['value'] else '\x04'
        packet = APIPacket(address)
        self.xbee.send('D{0}'.format(channel), value, packet)

    def do_shutdown(self):
        if self._xbee is not None:
            self._xbee.close()

    @property
    def events(self):
        return ['xbee server']

    @property
    def xbee(self):
        if self._xbee is None:
            self._xbee = self._XBee_Class(self._device, 9600)
        return self._xbee

