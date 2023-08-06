from gadgets.rcl import parse_command
from nose.tools import eq_

class TestRCL(object):

    def test_simple(self):
        command = 'turn on living room light'
        event, message = parse_command(command)
        eq_(event, command)

    def test_with_time_units(self):
        command = 'turn on living room light 5 seconds'
        event, message = parse_command(command)
        eq_(event, 'turn on living room light')
        eq_(message, {'value': 5.0, 'units': 'seconds'})

    def test_with_time_units_with_for(self):
        command = 'turn on living room light for 5 seconds'
        event, message = parse_command(command)
        eq_(event, 'turn on living room light')
        eq_(message, {'value': 5.0, 'units': 'seconds'})

    def test_with_heat_units_with_for(self):
        command = 'heat fish tank to 70 F'
        event, message = parse_command(command)
        eq_(event, 'heat fish tank')
        eq_(message, {'value': 70.0, 'units': 'F'})

    def test_with_heat_units(self):
        command = 'heat fish tank 70 F'
        event, message = parse_command(command)
        eq_(event, 'heat fish tank')
        eq_(message, {'value': 70.0, 'units': 'F'})

    def test_with_volume_units(self):
        command = 'fill fish tank 3.3 liters'
        event, message = parse_command(command)
        eq_(event, 'fill fish tank')
        eq_(message, {'value': 3.3, 'units': 'liters'})

    def test_with_volume_units_with_to(self):
        command = 'fill fish tank to 3.3 liters'
        event, message = parse_command(command)
        eq_(event, 'fill fish tank')
        eq_(message, {'value': 3.3, 'units': 'liters'})