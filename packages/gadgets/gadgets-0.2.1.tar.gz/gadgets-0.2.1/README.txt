Gadgets - a physical computing framework
--------------------------------------------------------------------------------

Gadgets provides  a way  to control  physical devices  with python  on a
Beaglebone or a Raspberry PI (Raspberry Pi only has gpio functionality,
for now).  It provides an easy way to create a system that:

* Controls devices with the gpio, pwm, adc, and 1-wire interfaces
* Has an easy to use User Interface
* Can be distributed across many Beaglebones
* Uses RCL (Robot Command Language)
* Can run methods (a sequece of RCL commands)

Gadgets provides several classes that are useful for controlling various devices.
They are:

* Switch
* Valve
* Heater
* Cooler
* Motor

The simplest one is Switch.  Here is an example of how to set up a gadgets system
that uses Switch to control multiple devices.

The first thing to do is define the switches you are going to use with a dictionary

    >>> from gadgets.pins.beaglebone import pins
    >>> from gadgets import get_gadgets
    >>> arguments = {
    ...     "locations": {
    ...         "living room": {
    ...             "light": {
    ...             "type": "switch",
    ...             "pin": pins["gpio"][8][3]
    ...             },
    ...         "back yard": {
    ...             "sprinklers": {
    ...             "type": "switch",
    ...             "pin": pins["gpio"][8][11],
    ...             },
    ...         },
    ...     },
    ... }

    >>> gadgets = get_gadgets(arguments)
    >>> gadgets.start()

The above definition assumes you have connected some switch (perhaps
a transistor or a relay) to port 8, pin 3 on the Beaglebone, and perhaps
a transistor connected to port 8, pin 11.  The transistor would then be
connected to the solenoid valve that turns on the sprinklers (you will
probably not be able to connect the solenoid directly to your Beaglebone
because it would draw too much current and probably uses 24V AC).

One way you can turn on the light that you defined above is to open
another terminal and start a python prompt.

    >>> from gadgets import Sockets
    >>> s = Sockets()
    >>> s.send("turn on living room light")

The light you have connected to the Beaglebone should now turn on.

    >>> s.send("turn off living room light")

This, of course, turns the light off.  These two commands are examples of
RCL (Robot Command Language).

To turn on the sprinklers in the back yard for 15 minutes, you would send
this command:

    >>> s.send("turn on back yard sprinklers for 15 minutes")

You can also control the gadgets by using the built in curses based user-interface.
See gadgets.ui for more details.
