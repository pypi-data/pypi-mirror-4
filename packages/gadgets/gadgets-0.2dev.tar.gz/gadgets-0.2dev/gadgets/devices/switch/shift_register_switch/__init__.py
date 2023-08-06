from gadgets.devices.switch.shift_register_switch.shift_register_switch import ShiftRegisterSwitch, ShiftRegisterIOFactory
from gadgets.devices.switch.shift_register_switch.shift_register_server import ShiftRegisterServer


def shift_register_switch_factory(location, name, arguments, addresses, io_factory=None):
    if shift_register_switch_factory.server is None:
        """
        The first time a ShiftRegisterSwitch gets created a ShiftRegisterServer
        must be created and started.
        """
        shift_register_switch_factory.server = ShiftRegisterServer('', 'shift register server', addresses)
        shift_register_switch_factory.server.start()
    return ShiftRegisterSwitch(
        location=location,
        name=name,
        addresses=addresses,
        io_factory=ShiftRegisterIOFactory(addresses, arguments['channel']),
        on=arguments.get('on'),
        off=arguments.get('off'),
    )

shift_register_switch_factory.server = None
