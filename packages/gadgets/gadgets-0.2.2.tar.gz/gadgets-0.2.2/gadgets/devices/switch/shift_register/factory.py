from gadgets.devices.switch.switch import Switch
from gadgets.devices.switch.shift_register.io import ShiftRegisterIOFactory
from gadgets.devices.switch.shift_register.server import ShiftRegisterServer


def shift_register_switch_factory(location, name, arguments, addresses, io_factory=None):
    if shift_register_switch_factory.server is None:
        """
        The first time a ShiftRegisterSwitch gets created a ShiftRegisterServer
        must be created and started.
        """
        shift_register_switch_factory.server = ShiftRegisterServer('', 'shift register server', addresses, arguments)
        shift_register_switch_factory.server.start()
    channel = arguments['channel']
    shift_register_switch_factory.server.register_switch(channel)
    return Switch(
        location=location,
        name=name,
        addresses=addresses,
        io_factory=ShiftRegisterIOFactory(addresses, channel),
        on=arguments.get('on'),
        off=arguments.get('off'),
        momentary=arguments.get('momentary', False)
    )

shift_register_switch_factory.server = None
