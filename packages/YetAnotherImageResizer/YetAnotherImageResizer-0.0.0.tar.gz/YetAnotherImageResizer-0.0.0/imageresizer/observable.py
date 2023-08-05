from collections import defaultdict

class Observable (defaultdict):

    def __init__ (self):
        defaultdict.__init__(self, object)

    def emit (self, *args):
        '''Pass parameters to all observers and update states.'''
        for subscriber in self:
            response = subscriber(*args)
            self[subscriber] = response

    def subscribe (self, subscriber):
        '''Add a new subscriber to self.'''
        self[subscriber] = None

    def stat (self):
        '''Return a tuple containing the state of each observer.'''
        return tuple(self.values())

myObservable = Observable ()

# subscribe some inlined functions.
# myObservable[lambda x, y: x * y] would also work here.
myObservable.subscribe(lambda x, y: x * y)
myObservable.subscribe(lambda x, y: float(x) / y)
myObservable.subscribe(lambda x, y: x + y)
myObservable.subscribe(lambda x, y: x - y)

# emit parameters to each observer
myObservable.emit(6, 2)

# get updated values
print myObservable.stat()         # returns: (8, 3.0, 4, 12)
