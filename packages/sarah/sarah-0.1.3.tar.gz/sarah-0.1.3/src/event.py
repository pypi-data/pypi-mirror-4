class Event(object):
    def __init__(self):
        self.handlers = set()
    def unregister(self, handler):
        self.handlers.remove(handler)
    def register(self, handler):
        self.handlers.add(handler)
    def __call__(self, *args, **kwargs):
        for handler in self.handlers:
            handler(*args, **kwargs)

class ConditionalEvent(Event):
    def __init__(self, activate_cb=None, deactivate_cb=None):
        super(ConditionalEvent, self).__init__()
        self.activate_cb = activate_cb
        self.deactivate_cb = deactivate_cb
    def unregister(self, handler):
        super(ConditionalEvent, self).unregister(handler)
        if not self.handlers:
            self.deactivate_cb()
    def register(self, handler):
        if not self.handlers:
            self.activate_cb()
        super(ConditionalEvent, self).register(handler)

# vim: et:sta:bs=2:sw=4:
