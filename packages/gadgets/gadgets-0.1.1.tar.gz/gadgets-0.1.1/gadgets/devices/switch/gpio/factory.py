from gadgets.io import GPIOFactory
from gadgets.devices.switch.switch import Switch


def switch_factory(location, name, arguments, addresses, io_factory=None):
    if io_factory is None:
        io_factory = GPIOFactory(arguments['pin'], direction='out')
    return Switch(
        location=location,
        name=name,
        addresses=addresses,
        io_factory=io_factory,
        on=arguments.get('on'),
        off=arguments.get('off'),
        momentary=arguments.get('momentary', False)
    )
