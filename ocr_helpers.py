from d2vs.helpers import mouse_move
from d2vs.ocr import OCR


def cursor_scan(x1, y1, x2, y2, desired_text):
    """
    Drag the mouse smoothly through an area and try to quickly scan via OCR above the mouse
    to see when we've found our target...

    :param x1:
    :param y1:
    :param x2:
    :param y2:
    :param desired_text:
    :return:
    """
    mouse_move(618, 1329)  # hover over red health orb
    readings = OCR().read(406, 1116, 826, 1212, delay=.5)
    # print("is_in_game results:")
    # print(readings)
    return any(['life:' in text.lower() for _, text, _ in readings])

    pass