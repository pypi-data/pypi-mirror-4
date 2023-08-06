from gadgets.devices.switch.shift_register.io import ShiftRegisterIO

class XBeeIOFactory(object):
    
    def __init__(self, addresses, channel, address):
        self._addresses = addresses
        self._channel = channel
        self._address = address
    
    def __call__(self):
        return XBeeIO(self._addresses, self._channel, self._address)


class XBeeIO(ShiftRegisterIO):

    """
    Implements the gadgets.io interface for XBee switches.

    Why XBee?  Gadget systems can be distributed across many
    BeagleBones or Raspberry Pis.  However if all you need
    is some remote Switch objects, it may be cheaper to use
    xbee radios.  XBee series 2 modules have 9 gpio pins each, and
    by using API mode you can control multiple remote XBee modules
    with a single XBee coordinator connected to your Beaglebone
    or Raspberry Pi.  The XBee modules do not need to be connected
    to a microcontroller, so all you have to do is provide power.  
    That should be less expensive than buying a Raspberry Pi along with
    a power supply, sd card and WiFi dongle.

    NOTE:  In order to communicate in the XBee API mode, you must install
    pyctu:

        $ easy_install pyctu
    
    """

    def __init__(self, addresses, channel, address):
        self._address = address
        super(XBeeIO, self).__init__(addresses, channel)
    
    def _send(self, value):
        self._sockets.send(
            'xbee server',
            {'value': value, 'channel': self._channel, 'address': self._address}
        )
        self._status = value
