from os.path import exists, join, basename
from sys import argv

from pygame import mixer

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
        path = config.get(section, option)
        if not self.is_local_mode():
            installation_root = config.get("resources", "installation-path")
            installed_path = join(installation_root, path)
            if exists(installed_path):
                return installed_path
        elif exists(path):
            return path
        return None

    def is_local_mode(self):
        return "-l" in argv

    def subscribe_to(self, kind, callback):
        self.get_game().delegate.add_subscriber(kind, callback)

    def unsubscribe_from(self, kind, callback):
        self.get_game().delegate.remove_subscriber(kind, callback)

    def is_debug_mode(self):
        return "-d" in argv
