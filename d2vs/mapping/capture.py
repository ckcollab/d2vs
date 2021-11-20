import keyboard
import mss
import mss.tools
import numpy as np

from time import sleep
from cv2 import cv2


def map_capture():
    with mss.mss() as sct:
        # The screen part to capture
        monitor = {"top": 50, "left": 1705, "width": 850, "height": 480}

        # center seems to be... x=2130 y=290

        i = 2
        before_image_name = f"{i}-pre-map.png"
        after_image_name = f"{i}-post-map.png"
        diff_image_name = f"{i}-difference-map.png"

        # Grab the data
        sct_img = sct.grab(monitor)
        mss.tools.to_png(sct_img.rgb, sct_img.size, output=before_image_name)
        keyboard.press_and_release("tab")

        sleep(.075)

        sct_img = sct.grab(monitor)
        mss.tools.to_png(sct_img.rgb, sct_img.size, output=after_image_name)
        keyboard.press_and_release("tab")

        f1 = cv2.imread(before_image_name)
        f1 = cv2.cvtColor(f1, cv2.COLOR_BGR2GRAY)
        f2 = cv2.imread(after_image_name)
        f2 = cv2.cvtColor(f2, cv2.COLOR_BGR2GRAY)
        threshold = 0.1

        absdiff = cv2.absdiff(f1, f2)
        _, thresholded = cv2.threshold(absdiff, int(threshold * 255), 255, cv2.THRESH_BINARY)

        cv2.imwrite(diff_image_name, thresholded)
        print("Different pixels: %s" % np.count_nonzero(thresholded))


sleep(2)
map_capture()

#
# while True:
#     with mss.mss() as sct:
#         # The screen part to capture
#         monitor = {"top": 52, "left": 1707, "width": 850, "height": 480}
#         output = "sct-{top}x{left}_{width}x{height}.png".format(**monitor)
#
#         # Grab the data
#         sct_img = sct.grab(monitor)
#
#         # Save to the picture file
#         mss.tools.to_png(sct_img.rgb, sct_img.size, output=output)
#         print(output)
