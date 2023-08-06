
import time

from gadgets.gadget import Gadget
from gadgets.sockets import Sockets, Addresses, Broker
from gadgets.coordinator import Coordinator

from gadgets.devices.cooler.cooler_factory import cooler_factory
from gadgets.devices.heater.electric_heater_factory import electric_heater_factory
from gadgets.devices.switch import switch_factory, shift_register_switch_factory, xbee_factory
from gadgets.devices.motor.motor_factory import motor_factory
from gadgets.devices.input.factory import input_factory
from gadgets.devices.valve.valve_factory import ValveFactory

from gadgets.sensors import thermometer_factory


def get_gadgets(arguments, addresses=None):
    factory = GadgetsFactory(addresses=addresses)
    return factory(arguments)


class GadgetsFactory(object):

    def __init__(self, addresses=None, ensure_off=False):
        self._ensure_off = ensure_off
        if addresses is None:
            addresses = Addresses()
        self._addresses = addresses
        self._factories = {
            'valve': ValveFactory(),
            'switch': switch_factory,
            'xbee': xbee_factory,
            'shift register switch': shift_register_switch_factory,
            'motor': motor_factory,
            'electric heater': electric_heater_factory,
            'cooler': cooler_factory,
            'thermometer': thermometer_factory,
            'input': input_factory
        }

    def add_factory(self, name, factory):
        self._factories[name] = factory

    def __call__(self, gadget_arguments):
        output = []
        for location, arguments in gadget_arguments['locations'].iteritems():
            for name, device_arguments in arguments.iteritems():
                if 'type' not in device_arguments:
                    raise GadgetsError('type needed in arguments {0}'.format(device_arguments))
                factory = self._factories[device_arguments['type']]
                gadget = factory(location, name, device_arguments, self._addresses)
                output.append(gadget)
        return Gadgets(output, self._addresses, ensure_off=self._ensure_off)

class Gadgets(object):
    """
    Gadgets holds all the Gadget subclass instances and starts them
    up.  If this instance is configured as the master (by using
    'localhost' as the host name in Addresses), then it also starts
    up a Broker and a Coordinator.
    """

    def __init__(self, gadgets, addresses, ensure_off=False):
        self._gadgets = gadgets
        self._ensure_off = ensure_off
        self._addresses = addresses
        self.coordinator = None
        super(Gadgets, self).__init__()

    def add_gadget(self, gadget):
        self._gadgets.append(gadget)

    def start(self):
        if self._is_master:
            broker = Broker(self._addresses)
            broker.start()
            time.sleep(0.2)
            self.coordinator = Coordinator(self._addresses)
            self.coordinator.start()
        for gadget in self._gadgets:
            gadget.start()
        if self._is_master:
            self.coordinator.join()
        else:
            gadget.join()

    @property
    def _is_master(self):
        return 'localhost' in self._addresses.out_address
