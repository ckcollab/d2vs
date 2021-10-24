from .base import BaseModule


class PickIt(BaseModule):

    def __init__(self):
        # self.ocr = ocr
        self.search_area = None

    def on_screen_capture(self, screen_data):
        # do we care to look, even?
        if self.search_area:

            pass
