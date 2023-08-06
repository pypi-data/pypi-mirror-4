class Signal(object):

    def __init__(self):
        self.handlers = []

    def send(self, *args, **kwargs):
        for handler in self.handlers:
            handler(*args, **kwargs)

    def connect(self, handler):
        self.handlers.append(handler)

    def disconnect(self, handler):
        self.handlers.remove(handler)

    def disconnect_all(self):
        del self.handlers[:]


class Observable(object):

    def __init__(self, value=None):
        self.value = value
        self.listeners = []

    def __call__(self, *args):
        if len(args) == 0:
            return self.get()
        elif len(args) == 1:
            return self.set(args[0])
        else:
            raise TypeError('Observable.__init__ takes zero or one arguments (%d given)' % len(args))

    def set(self, value):
        self.value = value
        for listener in self.listeners:
            listener(value)

    def get(self):
        return self.value

    def subscribe(self, listener):
        self.listeners.append(listener)

    def unsubscribe(self, listener):
        self.listeners.remove(listener)

    def unsubscribe_all(self, listener):
        del self.listeners[:]
