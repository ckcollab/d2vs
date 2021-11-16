import numpy as np

from unittest import TestCase
from PIL import Image

from ..ocr import OCR


class SimpleScanningTestcases(TestCase):

    def setUp(self):
        self.ocr = OCR()

    def _img_to_np(self, path):
        img = Image.open(path)
        return np.asarray(img, dtype='uint8')

    def test_scanning_simple_works(self):
        readings = self.ocr.read(self._img_to_np("tests/test_data/simple/586_gold.png"))
        assert len(readings) == 1
        _, text, item_type = readings[0]
        assert text == "586 Gold"
        assert item_type == "Normal"

        readings = self.ocr.read(self._img_to_np("tests/test_data/simple/super_mana_potion.png"))
        assert len(readings) == 1
        _, text, item_type = readings[0]
        assert text == "Super Mana Potion"
        assert item_type == "Normal"

    def test_scanning_ethereal_works(self):
        assert False

    def test_segmentation_not_misgrouping_things(self):
        # Get a few images of lots of items near each other and confirm grouping is proper
        assert False
