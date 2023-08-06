from gadgets.devices.switch.switch import Switch
from gadgets.devices.switch.xbee.io import XBeeIOFactory
from gadgets.devices.switch.xbee.server import XBeeServer


def xbee_factory(location, name, arguments, addresses, io_factory=None):
    if xbee_factory.server is None:
        """
        """
        xbee_factory.server = XBeeServer('', 'shift register server', addresses, arguments['device'])
        xbee_factory.server.start()
    channel = arguments['channel']
    address = arguments['address']
    return Switch(
        location=location,
        name=name,
        addresses=addresses,
        io_factory=XBeeIOFactory(addresses, channel, address),
        on=arguments.get('on'),
        off=arguments.get('off'),
        momentary=arguments.get('momentary', False)
    )

xbee_factory.server = None

