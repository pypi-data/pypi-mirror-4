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

    def __init__(self, location, name, addresses):
        self._state = 0
        self._spi = None
        super(ShiftRegisterServer, self).__init__(location, name, addresses)

    @property
    def events(self):
        return ['shift register server']

    def event_received(self, event, message):
        channel = message['channel']
        if message['value']:
            self._state |= 1 << channel
        else:
            self._state &= ~(1 << channel)
        self.spi.writebytes([self._state])
        
    @property
    def spi(self):
        if self._spi is None:
            self._spi = self._SPI_Class(2, 0)
        return self._spi
