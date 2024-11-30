from .base import OCRTestCases
from d2vs.ocr import OCR


class SimpleScanningTestcases(OCRTestCases):

    def setUp(self):
        # self.ocr = OCR()
        pass

    def test_scanning_for_item_description_gets_correct_bounds(self):
        img = self.path_to_np_array("test/test_data/item_descriptions/templar_coat.png")
        assert False

