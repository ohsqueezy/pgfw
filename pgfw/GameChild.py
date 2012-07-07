from os.path import exists, join, basename, normpath, abspath
from sys import argv

from pygame import mixer
from pygame.locals import *

import Game

class GameChild:

    def __init__(self, parent=None):
        self.parent = parent

    def get_game(self):
        current = self
        while not isinstance(current, Game.Game):
            current = current.parent
        return current

    def get_configuration(self):
        return self.get_game().configuration

    def get_input(self):
        return self.get_game().input

    def get_screen(self):
        return self.get_game().display.get_screen()

    def get_audio(self):
        return self.get_game().audio

    def get_delegate(self):
        return self.get_game().delegate

    def get_resource(self, section, option):
        config = self.get_configuration()
        rel_path = config.get(section, option)
        for root in config.get("setup", "resources-search-path"):
            if self.is_shared_mode() and not self.is_absolute_path(root):
                continue
            path = join(root, rel_path)
            if (exists(path)):
                return path
        self.print_debug("Couldn't find resource: {0}, {1}".\
                                   format(section, option))

    def print_debug(self, statement):
        if self.is_debug_mode():
            print statement

    def is_absolute_path(self, path):
        return normpath(path) == abspath(path)

    def is_shared_mode(self):
        return "-s" in argv

    def subscribe_to(self, kind, callback):
        self.get_game().delegate.add_subscriber(kind, callback)

    def unsubscribe_from(self, kind, callback):
        self.get_game().delegate.remove_subscriber(kind, callback)

    def is_debug_mode(self):
        return "-d" in argv

    def get_user_event_id(self):
        return globals()[self.get_configuration().get("event",
                                                      "user-event-id")]

    def is_command(self, evt, cmd):
        name = self.get_configuration().get("event", "command-event-name")
        return evt.type == self.get_user_event_id() and evt.name == name and \
               evt.command == cmd
