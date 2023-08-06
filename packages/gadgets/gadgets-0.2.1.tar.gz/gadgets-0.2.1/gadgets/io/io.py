import abc

class IO(object):
    """
    All subclasses of Device have an 'io' property.  It should return
    an object that provides this interface.
    """
    
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def on(self):
        """
        turn on the io device
        """
        return

    @abc.abstractmethod
    def off(self):
        """
        turn the io device off
        """
        return

    @abc.abstractmethod
    def close(self):
        """
        close the io device
        """
        return

    @abc.abstractproperty
    def status(self):
        """
        status of the io device
        """
        return

    
