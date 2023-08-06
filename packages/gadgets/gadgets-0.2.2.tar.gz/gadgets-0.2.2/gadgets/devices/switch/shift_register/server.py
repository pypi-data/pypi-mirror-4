import operator
from gadgets import Gadget
from gadgets.io import GPIO
try:
    from spi import SPI
except ImportError:
    SPI = None

    
class ShiftRegisterServer(Gadget):
    """
    If a gadgets system has multiple ShiftRegisterSwitch objects
    you don't want them conflicting with each other when writing
    to the register's spi interface.  ShiftRegisterServer takes care
    of all spi writes and eliminates any conflicts.
    """

    _SPI_Class = SPI #this may be switched to something else for testing
    _direction = 'output'

    def __init__(self, location, name, addresses, arguments):
        self._highest_channel = 0
        self._state = 0
        self._spi = None
        self._shift_registers = None
        self._bus = arguments.get('bus', 2) #works for beaglebone, pass in 0 for rpi
        self._device = arguments.get('device', 0)
        super(ShiftRegisterServer, self).__init__(location, name, addresses)

        
    def event_received(self, event, message):
        """
        This is the entry point for each new message.
        """
        if event == 'startup':
            value = self._get_bytes()
            self.spi.writebytes(value)
            return
        channel = message.get('channel')
        if channel is not False:
            self._toggle_bit(message['value'], channel)
            values = self._get_bytes()
            self.spi.writebytes(values)

    def do_shutdown(self):
        self._state = 0
        values = self._get_bytes()
        self.spi.writebytes(values)

    def register_switch(self, channel):
        """
        If the user configures a system with only two ShiftRegisterSwitch
        objects, but one of them uses, say,  channel 8, then there must be
        two physical shift registers in use with a bunch of unused pins.
        This function allows this server to send the correct number of
        characters to the spi interface (once char per chip).
        """
        if channel >= self._highest_channel:
            self._highest_channel = channel

    @property
    def events(self):
        return ['shift register server', 'startup']

    @property
    def shift_registers(self):
        """
        return the number of shift registers
        """
        if self._shift_registers is None:
            self._shift_registers = ((self._highest_channel) / 8) + 1
        return self._shift_registers

    def _get_bytes(self):
        """
        divide self._state into 8 bit values, for example:

        0b11100000011  ->   [0b111, 0b11]
        """
        bytes_list = [(self._state >> (i * 8)) & 255 for i in xrange(self.shift_registers)]
        bytes_list.reverse()
        return bytes_list

    def _toggle_bit(self, value, channel):
        """
        if value is True and channel is 3, then:
        0b00000000
        goes to:
        0b00001000
        """
        if value:
            self._state |= 1 << channel
        else:
            self._state &= ~(1 << channel)
        
    @property
    def spi(self):
        if self._spi is None:
            self._spi = self._SPI_Class(self._bus, self._device)
            self._spi.msh = 1000000 #the python module is limited in how fast it can send
        return self._spi
