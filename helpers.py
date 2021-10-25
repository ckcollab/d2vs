"""
We need to wrap each mouse move, pixel grab, etc. (anything dealing with coordinates) so we can
attach our own coordinate system handlers, to handle different resolutions.
"""
from time import sleep
import keyboard
import pyautogui


RESOLUTIONS = {
    "1080p": (1920, 1080),
    "1440p": (2560, 1440),
}
CURRENT_RESOLUTION_WIDTH, CURRENT_RESOLUTION_HEIGHT = pyautogui.size()


def coord_translation(x, y, original=RESOLUTIONS["1440p"], new=(CURRENT_RESOLUTION_WIDTH, CURRENT_RESOLUTION_HEIGHT)):
    """
    Converts a coordinate from one resolution to another, defaulting to whatever the screen size is

    :param x: x from original resolution
    :param y: y from original resolution
    :param original_resolution: the original resolution the coordinate was taken from; defaults to 1440p
    :param new_resolution: the new resolution the coordinate will be used in; defaults to current resolution
    :return:
    """
    assert original in RESOLUTIONS.values()
    assert new in RESOLUTIONS.values()
    if original == new:
        return x, y  # no translation needed
    translation = int((x * new[0]) / original[0]), int((y * new[1]) / original[1])
    # print(f"translation: {x}, {y} into {translation[0]}, {translation[1]}")
    return translation


def mouse_move(x, y, delay=.1):
    sleep(delay)
    # print(f"??????? orig {x}, {y}")
    # print(*coord_translation(x, y))
    pyautogui.moveTo(*coord_translation(x, y))


# def click(x, y, delay=.1, button=mouse.Button.LEFT):
def click(x, y, delay=.1, button="left"):
    # mouse.move(x, y)
    # sleep(delay)
    # mouse.click(button, .1)
    sleep(delay)
    x, y = coord_translation(x, y)
    pyautogui.click(x=x, y=y, button=button)


def shift_attack(x, y, duration=1.0):
    keyboard.press("shift")
    mouse_move(x, y)  # our internal func, no coord translation needed
    sleep(.01)
    pyautogui.mouseDown()
    sleep(duration)
    pyautogui.mouseUp()
    keyboard.release("shift")




# def ensure_numlock_off():
#     if _get_numlock_state():
#         pyautogui.press('numlock')
#
#
# def _get_numlock_state():
#     import ctypes
#     hllDll = ctypes.WinDLL ("User32.dll")
#     VK_NUMLOCK = 0x90
#     return hllDll.GetKeyState(VK_NUMLOCK)
