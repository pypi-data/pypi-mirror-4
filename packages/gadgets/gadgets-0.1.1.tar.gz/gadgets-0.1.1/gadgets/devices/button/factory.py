from gadgets.devices.button.io import ButtonPollerFactory
from gadgets.devices.button.button import Button


def button_factory(location, name, arguments, addresses, io_factory=None):
    if io_factory is None:
        io_factory = ButtonPollerFactory(location, name, addresses, arguments['pin'])
    return Button(
        location=location,
        name=name,
        addresses=addresses,
        io_factory=io_factory,
    )