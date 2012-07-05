from os import mkdir
from os.path import exists, join
from sys import exc_info
from time import strftime

from pygame import image

from GameChild import *
from Input import *

class ScreenGrabber(GameChild):

    def __init__(self, game):
        GameChild.__init__(self, game)
        self.subscribe_to(Input.command_event, self.save_display)

    def save_display(self, event):
        if event.command == "capture-screen":
            directory = self.get_resource("capture-path")
            try:
                if not exists(directory):
                    mkdir(directory)
                name = self.build_name()
                path = join(directory, name)
                capture = image.save(self.get_screen(), path)
                print "Saved screen capture to %s" % directory + name
            except:
                print "Couldn't save screen capture to %s, %s" % \
                      (directory, exc_info()[1])

    def build_name(self):
        config = self.get_configuration()
        prefix = config["capture-file-name-format"]
        extension = config["capture-extension"]
        return strftime(prefix) + extension
