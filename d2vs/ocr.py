import easyocr
import os
import numpy as np
import traceback

from PIL import Image
from time import time

import cv2

from .constants import ITEM_TYPES


BASE_PATH = os.path.dirname(os.path.realpath(__file__))


class OCR:
    def __init__(self):
        self.reader = easyocr.Reader(
            ['en'],
            model_storage_directory=os.path.join(BASE_PATH, 'ocr_model'),
            user_network_directory=os.path.join(BASE_PATH, 'ocr_network'),
            recog_network='d2rg',
        )

        # Just in case we want to save training images..
        os.makedirs('ocr_training', exist_ok=True)

        # default to the next file # in the list or start at 1
        # (files will be 0001, 0002, 0003 + labels.csv, so len() on this works great)
        self.debug_image_counter = len(os.listdir('ocr_training')) or 1

    def read(self, screen_data, x1=None, y1=None, x2=None, y2=None, save_debug_images=False, width_ths=1.5):
        """
        Scans an area and returns the bounded text boxes, as well as a guess for the Item Type.

        :param screen_data: the data to OCR, which can be: Pillow Image, a filename, np array of pixel data
        :param x1:
        :param y1:
        :param x2:
        :param y2:
        :param save_debug_images: If True debug images are saved for machine learning later, to ocr_training/
        :param width_ths: Maximum horizontal distance to merge boxes; default = 0.6; useful to try a couple values to check for items!
        :return:
        """
        # Convert input data to something we like (np array w/ BGR data, not RGB)
        if isinstance(screen_data, str):
            screen_data = cv2.imread(screen_data)

        if not isinstance(screen_data, np.ndarray):
            screen_data = np.asarray(screen_data, dtype='uint8')
            if screen_data.shape[2] == 4:  # we have an alpha channel
                screen_data = cv2.cvtColor(screen_data, cv2.COLOR_RGBA2BGR)
            else:
                screen_data = cv2.cvtColor(screen_data, cv2.COLOR_RGB2BGR)

        height, width, color_channels = screen_data.shape

        # defaults should be full width/height if not given
        if x1 is None:
            x1 = 0
        if y1 is None:
            y1 = 0
        if x2 is None:
            x2 = width
        if y2 is None:
            y2 = height

        bounds = self.reader.readtext(
            # Cut window up, only do certain part
            screen_data[y1:y2, x1:x2],

            # Maximum shift in y direction. Boxes with different level should not be merged. default = 0.5
            ycenter_ths=0.1,

            # Maximum horizontal distance to merge boxes. default = 0.5
            width_ths=width_ths,

            # Amount of boundary space around the letter/word when the coordinates are returned
            # low_text=0.3,

            # Amount of distance allowed between two characters for them to be seen as a single word
            # link_threshold=0.6,

            # No idea what decoder/beamWidth do :( tweaking to try and not have items merged when scanning..
            # decoder='beamsearch',
            # beamWidth=6,

            # Following settings have no effect without this set to true!?
            # paragraph=False,
            # x_ths=1.0,
        )

        # # TODO: Just recognize? faster? no segmentation?
        # img, img_cv_grey = reformat_input(screen_data)
        #
        # bounds = self.reader.recognize(
        #     # Cut window up, only do certain part
        #     img_cv_grey[y1:y2, x1:x2],
        # )

        annotated_bounds = []
        for (top_left, top_right, bottom_right, bottom_left), text, _ in bounds:
            # from the left to the right, right down the center, only a couple rows of pixels (through the center)
            center_y = int(y1 + top_left[1] + ((bottom_right[1] - top_left[1]) / 2))
            row_data = screen_data[center_y - 1:center_y + 1, int(x1 + top_left[0]):int(x1 + bottom_right[0])]

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
                    item_cutout = screen_data[y1 + top_left[1]: y1 + bottom_right[1], x1 + top_left[0]: x1 + bottom_right[0]]
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
