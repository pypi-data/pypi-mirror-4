from gadgets.devices.input.io import InputPollerFactory
from gadgets.devices.input.adc import ADCPollerFactory
from gadgets.devices.input.input import Input


def input_factory(location, name, arguments, addresses, io_factory=None):
    input_type = arguments.get('input_type')
    if io_factory is None and (input_type == 'gpio' or input_type is None):
        io_factory = InputPollerFactory(location, name, addresses, arguments)
    elif io_factory is None and (input_type == 'adc'):
        io_factory = ADCPollerFactory(location, name, addresses, arguments)
    return Input(
        location=location,
        name=name,
        addresses=addresses,
        io_factory=io_factory,
    )
