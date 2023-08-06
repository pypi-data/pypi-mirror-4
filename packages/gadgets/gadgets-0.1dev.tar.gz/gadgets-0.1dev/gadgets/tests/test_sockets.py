import time, threading, random
from nose.tools import eq_
from gadgets import Addresses, Sockets, Broker

class TestSockets(object):

    def test_broker(self):
        p = random.randint(3000, 50000)
        addresses = Addresses(in_port=p, out_port=p+1)
        broker = Broker(addresses)
        sockets = Sockets(addresses)
        broker.start()
        time.sleep(0.5)
        sockets.send('shutdown', {})
        time.sleep(1)
        

    
