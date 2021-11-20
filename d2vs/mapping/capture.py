from glob import glob

import imutils
import keyboard
import mss
import mss.tools
import numpy as np

from time import sleep
from cv2 import cv2


def mask_image(img, color, background="None"):
    range_start, range_end = color_rgb_to_bgr_range(color)
    img_mask = cv2.inRange(img, range_start, range_end)

    # expand what we found to cover the whole thing, make the whole blur part of the mask via threshold
    img_mask = cv2.blur(img_mask, (3, 3))
    _, img_mask = cv2.threshold(img_mask, int(0.1 * 255), 255, cv2.THRESH_BINARY)

    if background == "None":
        return cv2.bitwise_and(img, img, mask=255 - img_mask)
    else:
        return cv2.bitwise_and(img, img, mask=255 - img_mask)

def color_rgb_to_bgr_range(color, range=30):
    r, g, b = color
    offset = int(range / 2)
    # return (b - offset, g - offset, r - offset), (b + offset, g + offset, r + offset)
    return (b - 12, g - 4, r - 4), (b + 12, g + 4, r + 4)







def map_capture(label=1):
    with mss.mss() as sct:
        # The screen part to capture
        # monitor = {"top": 50, "left": 1705, "width": 850, "height": 480}  # this gets everything including game name
        monitor = {"top": 65, "left": 1705, "width": 850, "height": 465}  # this skips over difficulty/area, if game name/pass already hidden

        # center seems to be... x=2130 y=290

        # i = 1  # setting this manually for now..
        before_image_name = f"captures/{label}-pre-map.png"
        after_image_name = f"captures/{label}-post-map.png"
        diff_image_name = f"captures/{label}-difference-map.png"
        result_image_name = f"captures/{label}-result.png"

        while True:  # TODO: set some number of max retries instead..
            # Grab the data
            sct_img = sct.grab(monitor)
            mss.tools.to_png(sct_img.rgb, sct_img.size, output=before_image_name)
            keyboard.press_and_release("tab")

            sleep(.075)

            sct_img = sct.grab(monitor)
            mss.tools.to_png(sct_img.rgb, sct_img.size, output=after_image_name)
            keyboard.press_and_release("tab")

            # read our original image without map
            f1 = cv2.imread(before_image_name)
            f1 = cv2.cvtColor(f1, cv2.COLOR_BGR2GRAY)

            # read our image with map
            f2 = cv2.imread(after_image_name)

            # remove shit from mini map
            # f2 = mask_image(f2, (0x1F, 0x7F, 0xEC))  # player marker
            # f2 = mask_image(f2, (0x21, 0x88, 0xFD))  # player marker
            f2 = mask_image(f2, (0x20, 0x84, 0xF6))  # player marker
            f2 = mask_image(f2, (0x44, 0x70, 0x74))  # merc marker


            # f2 = mask_image(f2, (0xEC, 0x7F, 0x1F))  # player marker
            # f2 = mask_image(f2, (0xFD, 0x88, 0x21))  # player marker
            # f2 = mask_image(f2, (0xFC, 0x87, 0x21))  # player marker


            # f2 = mask_image(f2, (0xEC, 0x7F, 0x1F))  # player marker
            # f2 = mask_image(f2, (0x44, 0x70, 0x74))  # merc marker

            # cv2.imshow('thing', f2)
            # cv2.waitKey()
            # exit()

            # we removed colored shit from map, back to grayscale
            f2 = cv2.cvtColor(f2, cv2.COLOR_BGR2GRAY)






            # pull player/merc icons from mini map
            # player_map_marker = cv2.inRange(f2, 0x2188FD, 0x2188FD)
            # merc_map_marker = cv2.inRange(f2, 0x447074, 0x447074)
            #
            # # f1 = cv2.bitwise_and(f1, f1, mask=255 - player_map_marker)
            # # f1 = cv2.bitwise_and(f1, f1, mask=255 - merc_map_marker)
            # #
            # # f2 = cv2.bitwise_and(f2, f2, mask=255 - player_map_marker)
            # # f2 = cv2.bitwise_and(f2, f2, mask=255 - merc_map_marker)
            #
            #
            #
            # f1 = cv2.bitwise_xor(f1, f2, mask=255 - player_map_marker)
            # f2 = cv2.bitwise_xor(f1, f2, mask=255 - merc_map_marker)





            # f1 = mask_image(f1, 0x2188FD)  # player marker
            # f1 = mask_image(f1, 0x447074)  # merc marker
            #
            # f2 = mask_image(f2, 0x2188FD)  # player marker
            # f2 = mask_image(f2, 0x447074)  # merc marker
            #
            # cv2.imshow('thing', f2)
            # cv2.waitKey()
            #
            # f2 = cv2.bitwise_xor(f1, f2)








            threshold = 0.11

            #

            # # This gets our map layer, masking out stash, players, npcs, npc names, etc.
            # # f2
            # # npc_name_mask = cv2.inRange(f2, 0xC7B377, 0xC7B377)
            # #
            # # processed_f2 = cv2.bitwise_and(f2, f2, mask=255 - npc_name_mask)
            #
            # # player_map_marker = cv2.inRange(f2, 0x2188FD, 0x2188FD)
            # # processed_f2 = cv2.bitwise_and(f2, f2, mask=player_map_marker)
            # merc_map_marker = cv2.inRange(f2, 0x447074, 0x447074)
            # # processed_f2 = cv2.bitwise_and(f2, f2, mask=merc_map_marker)
            # processed_f2 = cv2.bitwise_or(f1, f2, mask=merc_map_marker)



            # cv2.imshow('Result', processed_f2)
            # cv2.waitKey(0)



            # absdiff = cv2.absdiff(f1, f2)
            absdiff = cv2.absdiff(f1, f2)
            _, thresholded = cv2.threshold(absdiff, int(threshold * 255), 255, cv2.THRESH_BINARY)





            # cv2.imshow('Result', absdiff)
            # cv2.waitKey(0)




            different_pixels = np.count_nonzero(thresholded)
            print(f"Different pixels: {different_pixels}")

            # if different_pixels > 110000:
            #     print("??? Bad capture? during a teleport? monster walked in the way? retry...")
            #     exit()
            #     continue
            # else:
            #     break
            break


        cv2.imwrite(diff_image_name, thresholded)


        def unsharp_mask(img, blur_size=(9, 9), imgWeight=1.5, gaussianWeight=-0.5):
            gaussian = cv2.GaussianBlur(img, (5, 5), 0)
            return cv2.addWeighted(img, imgWeight, gaussian, gaussianWeight, 0)

        img = cv2.blur(thresholded, (5, 5))
        img = unsharp_mask(img)
        img = unsharp_mask(img)
        img = unsharp_mask(img)

        # hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        # h, s, v = cv2.split(hsv)

        thresh = cv2.adaptiveThreshold(img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2)
        contours, heirarchy = cv2.findContours(thresh.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        cnts = sorted(contours, key=cv2.contourArea, reverse=True)
        # for cnt in cnts:
        canvas_for_contours = thresh.copy()
        cv2.drawContours(thresh, cnts[:-1], 0, (0, 255, 0), 3)
        cv2.drawContours(canvas_for_contours, contours, 0, (0, 255, 0), 3)
        # cv2.imshow('Result', canvas_for_contours - thresh)
        cv2.imwrite(result_image_name, canvas_for_contours - thresh)
        # cv2.waitKey(0)


def map_stitch(*files):
    print(files)
    images = []
    for f in files:
        image = cv2.imread(f)
        images.append(image)

    stitcher = cv2.Stitcher_create(cv2.Stitcher_SCANS)  # scans instead of panorama mode
    stitcher.setPanoConfidenceThresh(0.7)  # might be too aggressive for real examples


    (status, stitched) = stitcher.stitch(images)

    if status != cv2.Stitcher_OK:
        print("Can't stitch images, error code = %d" % status)
        exit(-1)

    cv2.imshow('Result', stitched)
    cv2.waitKey(0)



# Do captures
# for n in range(15):
#     sleep(2)
#     map_capture(n)

# Do stitching
# map_stitch(*glob("captures/*-result.png"))
map_stitch(*glob("captures/*-difference*.png"))

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
