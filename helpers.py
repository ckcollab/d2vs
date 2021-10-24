"""
We need to wrap each mouse move, pixel grab, etc. (anything dealing with coordinates) so we can
attach our own coordinate system handlers, to handle different resolutions.
"""
from time import sleep
import keyboard
import pyautogui


def mouse_move(x, y, delay=.1):
    sleep(delay)
    pyautogui.moveTo(x, y)


# def click(x, y, delay=.1, button=mouse.Button.LEFT):
def click(x, y, delay=.1, button="left"):
    # mouse.move(x, y)
    # sleep(delay)
    # mouse.click(button, .1)
    sleep(delay)
    pyautogui.click(x=x, y=y, button=button)


def shift_attack(x, y, duration=1.0):
    keyboard.press("shift")
    pyautogui.moveTo(x, y)
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
