import numpy as np

from d2vs.helpers import mouse_move
from d2vs.ocr import OCR


def is_corpse_on_ground():
    """
    Moves mouse to center of screen and looks for "_____'s Corpse" text

    :return: True if corpse is on ground
    """
    # Hover over where body should be..
    mouse_move(1276, 672)

    # Try a couple times..
    for _ in range(2):
        # Scan it
        results = OCR().read(790, 420, 1760, 520, delay=.5)
        # 'corpse' any where in text all lowercased?
        if any('corpse' in text.lower() for _, text, _ in results):
            return True
    return False


def is_at_character_select_screen():
    """
    Checks the screen for the "Play" button to confirm we're on the character select screen.

    NOTE! We are looking for the "Play" button in such a way that it only works for ONLINE.

    :return: True if we can see the text "Play" in the right spot
    """
    readings = OCR().read(1000, 1270, 1145, 1320)
    # print("is_at_character_select_screen results:")
    # print(readings)
    return readings and readings[0][1] == "Play"


def is_in_queue():
    """
    Reads the center of the screen looking for the word "queue" anywhere..

    :return: True if we see the text "queue"
    """
    # Get mouse out of the way..
    mouse_move(1, 1)
    # print(f"OCR ID in is_in_queue: {id(OCR())}")
    readings = OCR().read(775, 420, 1550, 850, delay=.5)
    # print("is_in_queue results:")
    # print(readings)
    return any(['queue' in text.lower() for _, text, _ in readings])
        # print("IN QUEUE!")


def is_mercenary_alive():
    """
    Looks for mercenary green health bar

    :return: True if mercenary health bar found
    """
    left = 40
    right = 80
    merc_healthbar_slice = OCR().screen_data[30:31, left:right]
    green_pixel_count = np.sum(merc_healthbar_slice == [0x00, 0x84, 0x00])
    is_alive = green_pixel_count > 40
    # print(f"is_mercenary_alive pixel count for 0x008400 ({is_alive}):")
    # print(green_pixel_count)
    # should be a shitload of green pixels in this region
    return is_alive


def is_in_game():
    """
    Hover over life globe and see if any text can be OCR'd ... probably a better way to do this ...

    :return: True if we can see "Life:" text when hovering where health orb should be
    """
    mouse_move(618, 1329)  # hover over red health orb
    mouse_move(618, 1335)  # sometimes life isn't showing until you move mouse a bit..
    readings = OCR().read(406, 1116, 826, 1212, delay=.5)
    # print("is_in_game results:")
    # print(readings)
    return any(['life:' in text.lower() for _, text, _ in readings])
