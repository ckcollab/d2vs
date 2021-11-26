import keyboard
import mss
import mss.tools
import numpy as np

from cv2 import cv2
from glob import glob
from time import sleep


def mask_image(img, color, background="None"):
    range_start, range_end = color_rgb_to_bgr_range(color)
    img_mask = cv2.inRange(img, range_start, range_end)

    # expand what we found to cover the whole thing, make the whole blur part of the mask via threshold
    img_mask = cv2.blur(img_mask, (4, 4))
    _, img_mask = cv2.threshold(img_mask, int(0.1 * 255), 255, cv2.THRESH_BINARY)

    if background == "None":
        return cv2.bitwise_and(img, img, mask=255 - img_mask)
    else:
        return cv2.bitwise_and(img, img, mask=255 - img_mask)


def color_rgb_to_bgr_range(color, range=1):
    r, g, b = color
    offset = int(range / 2)
    # return (b - offset, g - offset, r - offset), (b + offset, g + offset, r + offset)
    return (b - (12 * range), g - (8 * range), r - (8 * range)), (b + (12 * range), g + (8 * range), r + (8 * range))


def map_capture(label=0, map=None, unstitched_pool=None):
    # we want to return x/y as best as we can tell it
    current_x = None
    current_y = None

    unstitched_pool = unstitched_pool or []

    with mss.mss() as sct:
        # The screen part to capture
        # monitor = {"top": 50, "left": 1705, "width": 850, "height": 480}  # this gets everything including game name
        monitor = {"top": 65, "left": 1705, "width": 850, "height": 465}  # this skips over difficulty/area, if game name/pass already hidden
        center_x = int(monitor["width"] / 2)
        center_y = int(monitor["height"] / 2)

        # center seems to be... x=2130 y=290

        # i = 1  # setting this manually for now..
        before_image_name = f"captures/{label}-pre-map.png"
        after_image_name = f"captures/{label}-post-map.png"
        diff_image_name = f"captures/{label}-difference-map.png"
        result_image_name = f"captures/{label}-result.png"
        map_image_name = f"captures/{label}-map.png"

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

            # After removing stuff add
            original_f2 = f2.copy()

            # we removed colored shit from map, back to grayscale
            f2 = cv2.cvtColor(f2, cv2.COLOR_BGR2GRAY)

            threshold = 0.11
            absdiff = cv2.absdiff(f1, f2)
            _, thresholded = cv2.threshold(absdiff, int(threshold * 255), 255, cv2.THRESH_BINARY)


            # done pulling out mini map, now work with colors..
            thresholded = cv2.cvtColor(thresholded, cv2.COLOR_GRAY2BGR)











            # TODO: Nov 20, try to do thresholded = cv2.cvtColor(thresholded, cv2.COLOR_GRAY2BGRA)
            #  (****with an alpha channel!****)











            # were there any warps here? highlight them!
            # range_start, range_end = color_rgb_to_bgr_range((0xD9, 0x58, 0xEB))  # gets top of warp
            # range_start, range_end = color_rgb_to_bgr_range((0xA2, 0x46, 0xEA))  # middle of warp
            # range_start, range_end = color_rgb_to_bgr_range((0xB5, 0x4C, 0xEB))  # middle of warp
            range_start, range_end = color_rgb_to_bgr_range((0x8D, 0x3C, 0xB2), range=1.5)  # middle of warp
            # range_start, range_end = (0xEB - 15, 0x58 - 15, 0xD9 - 15), (0xEA + 15, 0x46 + 15, 0xA2 + 15)
            warp_mask = cv2.inRange(original_f2, range_start, range_end)
            warp_mask = cv2.blur(warp_mask, (5, 5))
            _, warp_mask = cv2.threshold(warp_mask, int(0.1 * 255), 255, cv2.THRESH_BINARY)

            thresholded[warp_mask > 0] = [0xD9, 0x58, 0xEB]  # Where ever there is a warp color it in with da purps

            different_pixels = np.count_nonzero(thresholded)
            print(f"Different pixels: {different_pixels}")

            # If this is our first scan .. this is our "base point" where we pivot from and start our lil coordinate system.
            if label == 0:
                # Draw a big red circle that will stick around between images
                cv2.circle(thresholded, (center_x, center_y), 5, (0, 0, 255), -1)

                # cv2.imshow('Result', thresholded)
                # cv2.waitKey(0)
                # exit()
                current_x = 10_000
                current_y = 10_000

                map = thresholded

                # successful stitch means we can clear the list
                unstitched_pool = []
            else:
                # remove old green circles from stitched master image
                old_green_mask = cv2.inRange(map, (0, 255, 0), (0, 255, 0))
                map[old_green_mask > 0] = [0, 0, 0]
                if np.any(old_green_mask > 0):
                    print("%%%%%%%%%%%%%% seen ag reens")

                # draw new green circle in center where our player is
                cv2.circle(thresholded, (center_x, center_y), 5, (0, 255, 0), -1)

                # do stitching?
                stitcher = cv2.Stitcher_create(cv2.Stitcher_SCANS)  # scans instead of panorama mode
                stitcher.setPanoConfidenceThresh(0.65)  # 0.7 seems to work great for black marsh
                # stitcher.setSeamEstimationResol(1)
                # stitcher.setCompositingResol(1)

                status, stitched = stitcher.stitch([map, thresholded] + unstitched_pool)

                if status == cv2.Stitcher_OK:
                    map = stitched
                else:
                    print("Can't stitch images, error code = %d" % status)
                    # exit(-1)

                    unstitched_pool.append(thresholded)



                # location of green/red?
                # cv2.imshow('Result', map)
                # cv2.waitKey(0)
                # cv2.imshow('Result', cv2.inRange(map, (0, 255, 0), (0, 255, 0)))
                # cv2.waitKey(0)
                # exit()
                green_circle_coord = cv2.findNonZero(cv2.inRange(map, (0, 255, 0), (0, 255, 0)))
                red_circle_coord = cv2.findNonZero(cv2.inRange(map, (0, 0, 255), (0, 0, 255)))

                print(f"Green Circle Coord: {green_circle_coord}")
                print(f"Red Circle Coord: {red_circle_coord}")

                # dist_from_green_to_red = ...
                # direction = ...
                #
                # calculate_from_dist_and_dir_new_x_y = ...
            cv2.imwrite(map_image_name, map)

            # if different_pixels > 110000:
            #     print("??? Bad capture? during a teleport? monster walked in the way? retry...")
            #     exit()
            #     continue
            # else:
            #     break
            break

        cv2.imwrite(diff_image_name, thresholded)

        # # weird edge post processing stuff, probably removing this?
        # def unsharp_mask(img, blur_size=(9, 9), imgWeight=1.5, gaussianWeight=-0.5):
        #     gaussian = cv2.GaussianBlur(img, (5, 5), 0)
        #     return cv2.addWeighted(img, imgWeight, gaussian, gaussianWeight, 0)
        # img = cv2.blur(thresholded, (5, 5))
        # img = unsharp_mask(img)
        # img = unsharp_mask(img)
        # img = unsharp_mask(img)
        #
        # # hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        # # h, s, v = cv2.split(hsv)
        #
        # img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        #
        # thresh = cv2.adaptiveThreshold(img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2)
        # contours, heirarchy = cv2.findContours(thresh.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        # cnts = sorted(contours, key=cv2.contourArea, reverse=True)
        # # for cnt in cnts:
        # canvas_for_contours = thresh.copy()
        # cv2.drawContours(thresh, cnts[:-1], 0, (0, 255, 0), 3)
        # cv2.drawContours(canvas_for_contours, contours, 0, (0, 255, 0), 3)
        # # # cv2.imshow('Result', canvas_for_contours - thresh)
        # cv2.imwrite(result_image_name, canvas_for_contours - thresh)
        # # # cv2.waitKey(0)
        return current_x, current_y, map, unstitched_pool


def map_stitch(*files):
    print(files)
    images = []
    for f in files:
        image = cv2.imread(f)
        images.append(image)

    stitcher = cv2.Stitcher_create(cv2.Stitcher_SCANS)  # scans instead of panorama mode
    stitcher.setPanoConfidenceThresh(0.7)  # 0.7 seems to work great for black marsh
    # stitcher.setSeamEstimationResol(1)
    # stitcher.setCompositingResol(1)


    (status, stitched) = stitcher.stitch(images)

    if status != cv2.Stitcher_OK:
        print("Can't stitch images, error code = %d" % status)
        exit(-1)

    cv2.imshow('Result', stitched)
    cv2.waitKey(0)


# Do captures
# map = None
# unstitched_pool = []
# for n in range(15):
#     sleep(2)
#     # TODO: map_capture could return current_x, current_y
#     x, y, map, unstitched_pool = map_capture(n, map=map, unstitched_pool=unstitched_pool)
#
#     print(f"Current x = {x}, y = {y}")
#
# cv2.imshow('Result', map)
# cv2.waitKey(0)
# exit()


# Do stitching
# map_stitch(*glob("captures/*-result.png"))
map_stitch(*glob("captures/*-difference*.png")[:10])

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
