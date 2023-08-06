import time

class GadgetsError(Exception):
    """
    raises an Exception, and if initialized with
    a sockets object, will send the error message
    to the whole gadgets system.
    """

    def __init__(self, msg, sockets=None, uid=None):
        if sockets is not None:
            sockets.send('error', {'error': msg, 'id': uid})
            time.sleep(0.2) #give the socket time before the error is raised
        super(GadgetsError, self).__init__(msg)
        
        