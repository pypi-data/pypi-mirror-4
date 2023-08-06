import math, datetime, zmq


class VolumeConverter:
    """
    t = ((3.14 x dia^2) / (C x A)) x (h / (8 x g))^0.5

    Where
    t = time in seconds
    dia = diameter of tank in ft
    C = Orface coef. (0.7 to 0.91) I use 0.81 for a pipe penitrating the tank wall.
    A = aera of orface in sf
    h = height of water above outlet in ft
    g = gravitational constant (32.2)

    """
    def __init__(self, tank_radius, valve_radius, coefficient=0.81):
        tank_radius = tank_radius * 2.54  # convert to centimeters
        valve_radius = valve_radius * 2.54 # convert to centimeters
        self.coefficient = coefficient
        self.tank_area = math.pi * tank_radius ** 2
        valve_area = math.pi * valve_radius ** 2
        g = 9.806 * 100.0 #centimeters
        x = pow((2 / g), 0.5)
        self.k = (self.tank_area * x) / (valve_area * coefficient)
        self.valve_area = valve_area
        self.x = x

    def get_volume(self, starting_volume, time):
        starting_volume = starting_volume * 1000.0 #convert to cubic centimeters
        height = self._get_height(starting_volume)
        dh = math.fabs(((time / self.k) ** 2) - (2 * (time / self.k) * pow(height, 0.5)))
        return (self.tank_area * dh) / 1000.0
    
    def get_drain_time(self, starting_volume, volume):
        volume = 1000 * volume #convert to cubic centimeters
        starting_volume = starting_volume * 1000.0
        height_diff = self._get_height(volume)
        height = self._get_height(starting_volume)
        h2 = height - height_diff
        return (pow(height, 0.5) - pow(h2, 0.5)) * self.k

    def get_coefficient(self, starting_volume, volume, drain_time):
        hi = self._get_height(starting_volume * 1000.0)
        dh = self._get_height(volume * 1000.0)
        hf = hi - dh
        At = self.tank_area
        Av = self.valve_area
        t = drain_time
        x = self.x
        return ((At * x) / Av) * ((hi**0.5) - (hf**0.5)) / t

    def _get_height(self, volume):
        return volume / self.tank_area

def calibrate():
    vc = VolumeConverter(7.5, 0.1875)
    addr = 'tcp://brewery:5000'
    socket = context.socket(zmq.PUSH)
    socket.connect(addr)
    socket.send('fill tun 4')
    start = datetime.datetime.now()
    x = raw_input('Push enter when 2 liters has dispensed')
    end = datetime.datetime.now()
    socket.send('stop filling tun')
    delta = end - start
    t = delta.seconds + delta.microseconds/1000000.0
    coefficient = vc.get_coefficient(26.5, 2.0, t)


