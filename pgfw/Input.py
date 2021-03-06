from pygame import event, joystick as joy, key as keyboard
from pygame.locals import *

from GameChild import *

class Input(GameChild):

    def __init__(self, game):
        GameChild.__init__(self, game)
        self.joystick = Joystick()
        self.unsuppress()
        self.subscribe_to_events()
        self.build_key_map()

    def subscribe_to_events(self):
        self.subscribe_to(KEYDOWN, self.translate_key_press)
        self.subscribe_to(JOYBUTTONDOWN, self.translate_joy_button)
        self.subscribe_to(JOYAXISMOTION, self.translate_axis_motion)

    def suppress(self):
        self.suppressed = True

    def unsuppress(self):
        self.suppressed = False

    def build_key_map(self):
        key_map = {}
        for command, keys in self.get_configuration().items("keys"):
            key_map[command] = []
            if type(keys) == str:
                keys = [keys]
            for key in keys:
                key_map[command].append(globals()[key])
        self.key_map = key_map

    def translate_key_press(self, evt):
        self.print_debug("You pressed {0}, suppressed => {1}".\
                         format(evt.key, self.suppressed))
        if not self.suppressed:
            key = evt.key
            for cmd, keys in self.key_map.iteritems():
                if key in keys:
                    self.post_command(cmd)

    def post_command(self, cmd):
        eid = self.get_user_event_id()
        self.print_debug("Posting {0} command with id {1}".format(cmd, eid))
        name = self.get_configuration().get("event", "command-event-name")
        event.post(event.Event(eid, name=name, command=cmd))

    def translate_joy_button(self, evt):
        if not self.suppressed:
            button = evt.button
            config = self.get_configuration()
            if button == config["joy-advance"]:
                self.post_command("advance")
            if button == config["joy-pause"]:
                self.post_command("pause")

    def translate_axis_motion(self, evt):
        if not self.suppressed:
            axis = evt.axis
            value = evt.value
            if axis == 1:
                if value < 0:
                    self.post_command("up")
                elif value > 0:
                    self.post_command("down")
            else:
                if value > 0:
                    self.post_command("right")
                elif value < 0:
                    self.post_command("left")

    def is_command_active(self, command):
        if not self.suppressed:
            joystick = self.joystick
            if self.is_key_pressed(command):
                return True
            if command == "up":
                return joystick.is_direction_pressed(Joystick.up)
            elif command == "right":
                return joystick.is_direction_pressed(Joystick.right)
            elif command == "down":
                return joystick.is_direction_pressed(Joystick.down)
            elif command == "left":
                return joystick.is_direction_pressed(Joystick.left)
        else:
            return False

    def is_key_pressed(self, command):
        poll = keyboard.get_pressed()
        for key in self.key_map[command]:
            if poll[key]:
                return True

    def get_axes(self):
        axes = {}
        for direction in "up", "right", "down", "left":
            axes[direction] = self.is_command_active(direction)
        return axes


class Joystick:

    (up, right, down, left) = range(4)

    def __init__(self):
        js = None
        if joy.get_count() > 0:
            js = joy.Joystick(0)
            js.init()
        self.js = js

    def is_direction_pressed(self, direction):
        js = self.js
        if not js or direction > 4:
            return False
        if direction == 0:
            return js.get_axis(1) < 0
        elif direction == 1:
            return js.get_axis(0) > 0
        elif direction == 2:
            return js.get_axis(1) > 0
        elif direction == 3:
            return js.get_axis(0) < 0
