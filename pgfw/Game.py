import sys

import pygame
from pygame import display
from pygame.locals import *

from GameChild import *
from Animation import *
from Audio import *
from Display import *
from Configuration import *
from EventDelegate import *
from Input import *
from ScreenGrabber import *

class Game(GameChild, Animation):
    
    def __init__(self, installed_resources_path=".", config_rel_path=None):
        self.init_gamechild()
        self.installed_resources_path = installed_resources_path
        self.config_rel_path = config_rel_path
        self.set_configuration()
        self.init_animation()
        pygame.init()
        self.set_children()
        self.subscribe_to(QUIT, self.end)
        self.subscribe_to(Input.command_event, self.end)
        self.clear_queue()
        self.delegate.enable()

    def init_gamechild(self):
        GameChild.__init__(self)

    def set_configuration(self):
        self.configuration = Configuration(self.installed_resources_path,
                                           self.config_rel_path)

    def init_animation(self):
        Animation.__init__(self,
                           self.configuration.get("display", "frame-duration"))

    def set_children(self):
        self.set_display()
        self.set_delegate()
        self.set_input()
        self.set_audio()
        self.set_screen_grabber()

    def set_display(self):
        self.display = Display(self)

    def set_delegate(self):
        self.delegate = EventDelegate(self)

    def set_input(self):
        self.input = Input(self)

    def set_audio(self):
        self.audio = Audio(self)

    def set_screen_grabber(self):
        self.screen_grabber = ScreenGrabber(self)

    def sequence(self):
        self.delegate.dispatch_events()
        self.update()
        display.update()

    def update(self):
        pass

    def end(self, evt):
        if evt.type == QUIT or evt.command == "quit":
            self.stop()
