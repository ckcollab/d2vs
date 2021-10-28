import traceback
from uuid import uuid4

import easyocr
import os
import numpy as np
from PIL import Image
from time import sleep, time

from constants import ITEM_TYPES
from d2vs.helpers import coord_translation
from singleton import SingletonOptmizedOptmized
from window import Window


# class OCR:
class OCR(metaclass=SingletonOptmizedOptmized):
    def __init__(self):
        # self.window = Window()
        self.screen_data = None
        self.reader = easyocr.Reader(
            ['en'],
            model_storage_directory="./ocr_model",
            user_network_directory='./ocr_network',
            recog_network='d2rg',
            # download_enabled=False,
        )

        # Just in case we want to save training images..
        os.makedirs('ocr_training', exist_ok=True)

        # default to the next file # in the list or start at 1
        # (files will be 0001, 0002, 0003 + labels.csv, so len() on this works great)
        self.debug_image_counter = len(os.listdir('ocr_training')) or 1

    def set_screen_data(self, data):
        """This is called many times a second. If you want to scan the latest data, add a small delay
        before scanning."""
        self.screen_data = data

        # print(f"Set screen data, I am {id(self)}")

    def read(self, x1, y1, x2, y2, save_debug_images=False, delay=.1, coords_have_been_translated="Unset", width_ths=0.5):
        """
        Scans an area and returns the bounded text boxes, as well as a guess for the Item Type.

        Must have screen_data set before calling.

        These coordinates are by default NOT translated! These are raw coordinates, translate before calling this
        function or pass translate_coords=True

        :param x1:
        :param y1:
        :param x2:
        :param y2:
        :param save_debug_images: If True debug images are saved for machine learning later, to ocr_training/
        :param delay: how long to wait before scanning the area
        :param coords_have_been_translated: whether or not to translate coords from 1440p to current resolution, you must specify this!
        :param width_ths: Maximum horizontal distance to merge boxes; default = 0.6; useful to try a couple values to check for items!
        :return:
        """
        # Small delay so screen data can be written before we read..
        sleep(delay)

        assert coords_have_been_translated != "Unset", "You must set coords_have_been_translated to True or False!"

        # print("old:", x1, y1, x2, y2)

        if not coords_have_been_translated:
            x1, y1 = coord_translation(x1, y1)
            x2, y2 = coord_translation(x2, y2)

        # print("new:", x1, y1, x2, y2)

        # if x1 <= 0:
        #     x1 = 1
        # if y1 <= 0:
        #     y1 = 1
        # if x2 <= 0:
        #     x2 = 1
        # if y2 <= 0:
        #     y2 = 1

        assert self.screen_data is not None, "You must call OCR.set_screen_data before calling OCR.read"

        bounds = self.reader.readtext(
            # Cut window up, only do certain part
            self.screen_data[y1:y2, x1:x2],

            # Maximum shift in y direction. Boxes with different level should not be merged. default = 0.5
            ycenter_ths=0.08,

            # Maximum horizontal distance to merge boxes. default = 0.5
            width_ths=width_ths,

            # Amount of boundary space around the letter/word when the coordinates are returned
            low_text=0.3,

            # Amount of distance allowed between two characters for them to be seen as a single word
            # link_threshold=0.6,

            # No idea what decoder/beamWidth do :( tweaking to try and not have items merged when scanning..
            # decoder='beamsearch',
            # beamWidth=6,

            # Following settings have no effect without this set to true!?
            # paragraph=False,
            # x_ths=1.0,
        )

        annotated_bounds = []
        for (top_left, top_right, bottom_right, bottom_left), text, _ in bounds:
            # from the left to the right, right down the center, only a couple rows of pixels (through the center)
            center_y = int(y1 + top_left[1] + ((bottom_right[1] - top_left[1]) / 2))
            row_data = self.screen_data[center_y - 1:center_y + 1, int(x1 + top_left[0]):int(x1 + bottom_right[0])]

            color_counts = {}
            for item_type, colors in ITEM_TYPES.items():
                if len(colors) == 1:
                    count = np.sum(row_data == colors[0])
                elif len(colors) == 2:
                    count = np.sum(row_data == colors[0])
                    count += np.sum(row_data == colors[1])
                else:
                    raise Exception("Colors out of bounds, only allow 2 colors per item type at the moment..")
                # print(item_type, color, count)
                color_counts[item_type] = count

            # highest pixel count is most likely item type...
            item_type = max(color_counts, key=color_counts.get)

            # TODO: Only saving ethereal/socketed because that's the hardest to read... stop doing that?
            if save_debug_images and item_type == "Socketed/Ethereal":
                try:
                    item_cutout = self.screen_data[y1 + top_left[1] : y1 + bottom_right[1], x1 + top_left[0] : x1 + bottom_right[0]]
                    item_random_image_name = f"{self.debug_image_counter:04}-{time()}.png"
                    Image.fromarray(item_cutout).save(os.path.join('ocr_training', item_random_image_name))
                    with open(os.path.join('ocr_training', 'labels.csv'), 'a+') as f:
                        f.write(f"{item_random_image_name},{text}\n")
                    self.debug_image_counter += 1
                except TypeError:
                    print(f"Weird failure? text = {text}, top_left = {top_left}, top_right = {top_right}, bottom_right = {bottom_right}, bottom_left = {bottom_left}")
                    print(traceback.format_exc())

            annotated_bounds.append(
                ((top_left, top_right, bottom_right, bottom_left), text, item_type)
            )

        return annotated_bounds
