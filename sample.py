from time import sleep
from random import randint

from pgfw.Game import Game

# inheriting from Game allows you to customize your project
class SampleGame(Game):

    square_width = 30

    # update runs every frame, you can think of it as the mainloop
    def update(self):
        sleep(1)
        screen = self.get_screen()
        bounds = screen.get_size()
        screen.fill((0, 0, 0))
        screen.fill((255, 255, 255),
                    (randint(0, bounds[0]), randint(0, bounds[1]),
                     self.square_width, self.square_width))


if __name__ == '__main__':
    # the play method begins the project's animation
    SampleGame().play()
