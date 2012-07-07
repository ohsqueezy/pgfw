from pygame import event
from pygame.locals import *

from GameChild import *

class EventDelegate(GameChild):

    def __init__(self, game):
        GameChild.__init__(self, game)
        self.subscribers = dict()
        self.disable()

    def enable(self):
        self.enabled = True

    def disable(self):
        self.enabled = False

    def dispatch_events(self):
        if self.enabled:
            subscribers = self.subscribers
            for evt in event.get():
                kind = evt.type
                if kind in subscribers:
                    for subscriber in subscribers[kind]:
                        self.print_debug("Passing {0} to {1}".\
                                                   format(evt, subscriber))
                        subscriber(evt)
        else:
            event.pump()

    def add_subscriber(self, kind, callback):
        self.print_debug("Subscribing {0} to {1}".\
                                   format(callback, kind))
        subscribers = self.subscribers
        if kind not in subscribers:
            subscribers[kind] = list()
        subscribers[kind].append(callback)

    def remove_subscriber(self, kind, callback):
        self.subscribers[kind].remove(callback)
