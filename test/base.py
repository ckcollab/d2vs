from unittest import TestCase
from cv2 import cv2

from d2vs.ocr import OCR


class OCRTestCases(TestCase):

    def setUp(self):
        self.ocr = OCR()

    def assert_scan(self, path, expected_text, expected_item_type=None):
        readings = self.ocr.read(cv2.imread(path))
        assert len(readings) == 1
        _, text, item_type = readings[0]
        assert text == expected_text
        if item_type:
            assert item_type == expected_item_type
