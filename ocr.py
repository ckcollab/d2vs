import traceback
from uuid import uuid4

import easyocr
import os
import numpy as np
from PIL import Image
from time import sleep, time

from constants import ITEM_TYPES
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

    def read(self, x1, y1, x2, y2, save_debug_images=False, delay=.1):
        # Small delay so screen data can be written before we read..
        sleep(delay)

        assert self.screen_data is not None, "You must call OCR.set_screen_data before calling OCR.read"

        bounds = self.reader.readtext(
            # Cut window up, only do certain part
            self.screen_data[y1:y2, x1:x2],

            # Maximum shift in y direction. Boxes with different level should not be merged. default = 0.5
            ycenter_ths=0.1,

            # Maximum horizontal distance to merge boxes. default = 0.5
            width_ths=1.65,
        )

        annotated_bounds = []
        for (top_left, top_right, bottom_right, bottom_left), text, _ in bounds:


            # for test purposes, save this...

            # if text.lower() not in ["claws", "clasped orb", "naga"]:
            #     continue

            # with open(os.path.join('ocr_training', )) as f
            if save_debug_images:
                try:
                    item_cutout = self.screen_data[y1 + top_left[1] : y1 + bottom_right[1], x1 + top_left[0] : x1 + bottom_right[0]]
                    # item_random_image_name = f"{uuid4()}.png"
                    item_random_image_name = f"{self.debug_image_counter:04}-{time()}.png"
                    Image.fromarray(item_cutout).save(os.path.join('ocr_training', item_random_image_name))
                    with open(os.path.join('ocr_training', 'labels.csv'), 'a+') as f:
                        f.write(f"{item_random_image_name},{text}\n")
                    self.debug_image_counter += 1
                except TypeError:
                    print(f"Weird failure? text = {text}, top_left = {top_left}, top_right = {top_right}, bottom_right = {bottom_right}, bottom_left = {bottom_left}")
                    print(traceback.format_exc())

            # from the left to the right, right down the center, only 1 row of pixels (through the center)
            center_y = int(y1 + top_left[1] + ((bottom_right[1] - top_left[1]) / 2))
            # print(center_y, x1 + top_left[0], x1 + bottom_right[0])
            # for pixel in screen_data[center_y:center_y + 1, int(x1 + top_left[0]):int(x1 + bottom_right[0])]
            row_data = self.screen_data[center_y - 1:center_y + 1, int(x1 + top_left[0]):int(x1 + bottom_right[0])]
            # print("topleft:", top_left)
            # print("start:", x1 + top_left[0], center_y)
            # print(row_data)
            # print(text, ":::")
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

            # print(sorted(color_counts.items(), key=lambda item: item[1], reverse=True)[0][0])
            # item_type = sorted(color_counts.items(), key=lambda item: item[1], reverse=True)[0][0]
            item_type = max(color_counts, key=color_counts.get)

                # unique, counts = np.unique(row_data, return_counts=True)
                # count_dict = dict(zip(unique, counts))
                # print("Magic", count_dict[self.ITEM_TYPES["Magic"]])
                # print("Rare", count_dict[self.ITEM_TYPES["Rare"]])
                # print("Unique", count_dict[self.ITEM_TYPES["Unique"]])

            # colors, counts = np.unique(row_data, return_counts=True, axis=0)
            # print(list(zip(colors, counts)))


            # import time; time.sleep(1)
            # exit()

            annotated_bounds.append(
                ((top_left, top_right, bottom_right, bottom_left), text, item_type)
            )

        return annotated_bounds
