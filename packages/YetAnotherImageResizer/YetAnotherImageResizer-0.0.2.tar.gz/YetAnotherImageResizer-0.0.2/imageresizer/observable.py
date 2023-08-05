""" Module arbo contains the an implementation of the Oservable pattern. """
try:
    from collections import OrderedDict
except ImportError:
    # Hack for Python < 2.6
    # In this case, the order of the result via stat function are not sorted
    from collections import defaultdict as OrderedDict

class Observable (OrderedDict):
    """ Implements the Observable pattern. """

    def __init__ (self):
        OrderedDict.__init__(self)

    def emit (self, *args):
        """ Pass parameters to all observers and update states. """
        for subscriber in self:
            response = subscriber(*args)
            self[subscriber] = response

    def subscribe (self, subscriber):
        """ Add a new subscriber to self."""
        self[subscriber] = None

    def stat (self):
        """ Return a tuple containing the state of each observer.
        >>> myObservable = Observable()

        # subscribe some inlined functions.
        # myObservable[lambda x, y: x * y] would also work here.
        >>> myObservable.subscribe(lambda x, y: x * y)
        >>> myObservable.subscribe(lambda x, y: float(x) / y)
        >>> myObservable.subscribe(lambda x, y: x + y)
        >>> myObservable.subscribe(lambda x, y: x - y)

        # emit parameters to each observer
        >>> myObservable.emit(6, 2)

        # get updated values
        >>> print myObservable.stat()         # returns: (12, 3.0, 8, 4)
        (12, 3.0, 8, 4)
        """
        return tuple(self.values())

if __name__ == '__main__':
    import doctest
    doctest.testmod()
