from pygame import display, image

from GameChild import *

class Display(GameChild):

    def __init__(self, game):
        GameChild.__init__(self, game)
        self.config = self.get_configuration().get_section("display")
        self.set_screen()
        self.set_caption()
        self.set_icon()

    def set_screen(self):
        self.screen = display.set_mode(self.config["dimensions"])

    def set_caption(self):
        display.set_caption(self.config["caption"])

    def set_icon(self):
        if self.get_configuration().has_option("display", "icon-path"):
            path = self.get_resource("display", "icon-path")
            display.set_icon(image.load(path).convert_alpha())

    def get_screen(self):
        return self.screen

    def get_size(self):
        return self.screen.get_size()
