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

    Here is an example::

       >>> from gadgets import get_gadgets
       >>> arguments = {
       ...     "locations": {
       ...         "back yard": {
       ...             "gnome": {
       ...                 "type": "xbee",
       ...                 "channel": 3,
       ...                 "address": 0x0013A200409825C1,
       ...                 "device": '/dev/ttyUSB0',
       ...            }
       ...         }
       ...     }
       ... }
       >>> gadgets = get_gadgets(arguments)

    Address is the address of the XBee.  One way to find the address is
    to look at the label on the bottom of the module.  It will look
    something like this::

         ---- 004-revE
        |bar |0013A200
        |code|409825C1
         ----

    You combine the middle line (address high) with the bottom line (
    address low) to come up with the address that you use as an argument
    in the example above.

    Before any of the above will work, you need two XBee series 2
    modules - one connected to the BeagleBone or Raspberry Pi, and one
    one that is connected to the physical devices that you wish to
    control.  The one connected to the gadgets system must be running
    the 'coordinator api' firmware and the remote XBee(s) must be
    running 'router at' firmware.  They must also be configured with the
    same pan id.
    
    Now you can turn it on by creating a socket and giving the switches
    a RCL command::

    >>> from gadgets import Sockets
    >>> s = Sockets()
    >>> s.send("turn on back yard gnome")

    NOTE:  XBeeIO depends on pyctu for its XBee API mode communication::

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
