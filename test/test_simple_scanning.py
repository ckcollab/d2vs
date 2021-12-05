from .base import OCRTestCases
from d2vs.ocr import OCR


class SimpleScanningTestcases(OCRTestCases):

    def setUp(self):
        self.ocr = OCR()

    def test_scanning_simple_works(self):
        self._check_scan("test/test_data/simple/586_gold.png", "586 Gold", "Normal")
        self._check_scan("test/test_data/simple/super_mana_potion.png", "Super Mana Potion", "Normal")

    def test_scanning_ethereal_works(self):
        self._check_scan("test/test_data/ethereal/fascia.png", "Fascia", "Socketed/Ethereal")

    # def test_segmentation_not_misgrouping_things(self):
    #     # Get a few images of lots of items near each other and confirm grouping is proper
    #     assert False
    def test_scanning_magic_grand_charm_works(self):
        self._check_scan("test/test_data/magic/grand_charm_gold.PNG", "Grand Charm", "Magic")
