from d2vs.exceptions import ChickenException
from .base import BaseModule


class Chicken(BaseModule):

    def __init__(self):
        self.has_chickened = False
    #     self.GTFO = False

    def on_screen_capture(self, screen_data):
        pass
        # if not self.has_chickened:
        #
        #     # do our checks and raise this, MAYBE...
        #
        #     self.has_chickened = True
        #     raise D2VSChickenException()  # the actual game leaving happens in game bot thread...

        # TODO:
        #   - Check certain part of screen for red (or green, poisoned?!) health. if under a certain amount, freak out
        #   (scan from bottom to top, in case transparent globe is showing blood underneath or something)

    def on_game_start(self):
        # Reset at the start of each game...
        self.has_chickened = False
