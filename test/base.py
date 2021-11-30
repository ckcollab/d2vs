import numpy as np

from unittest import TestCase
from PIL import Image

from d2vs.ocr import OCR


class OCRTestCases(TestCase):

    def setUp(self):
        self.ocr = OCR()

    def _img_to_np(self, path):
        img = Image.open(path)
        return np.asarray(img, dtype='uint8')

    def _check_scan(self, path, expected_text, expected_item_type=None):
        readings = self.ocr.read(self._img_to_np(path))
        assert len(readings) == 1
        _, text, item_type = readings[0]
        assert text == expected_text
        if item_type:
            assert item_type == expected_item_type

    def assert_readings_match_expected(self, readings, expected):
        text = "\n".join([line for _, line, _ in readings])
        print(text)
        print(text)
        assert text == expected
        # for _, text, _ in readings:
        #     buffer +=