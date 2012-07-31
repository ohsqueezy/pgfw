from os import makedirs
from os.path import exists, join
from sys import exc_info
from time import strftime

from pygame import image

from GameChild import *
from Input import *

class ScreenGrabber(GameChild):

    def __init__(self, game):
        GameChild.__init__(self, game)
        self.subscribe_to(self.get_custom_event_id(), self.save_display)

    def save_display(self, event):
        if self.is_command(event, "capture-screen"):
            directory = self.get_configuration().get("screen-captures", "path")
            try:
                if not exists(directory):
                    makedirs(directory)
                name = self.build_name()
                path = join(directory, name)
                capture = image.save(self.get_screen(), path)
                self.print_debug("Saved screen capture to {0}".format(path))
            except:
                self.print_debug("Couldn't save screen capture to {0}, {1}".\
                                 format(directory, exc_info()[1]))

    def build_name(self):
        config = self.get_configuration().get_section("screen-captures")
        prefix = config["file-name-format"]
        extension = config["file-extension"]
        return "{0}.{1}".format(strftime(prefix), extension)
