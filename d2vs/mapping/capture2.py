"""
TODO:
  [ ] hsv capture of merc/player to filter it out
  [ ] stitch images together using affine
  [ ] get rid of moving things by adding a second diff
"""
from glob import glob
from typing import NamedTuple

import imageio
import keyboard
import mss
import mss.tools

from time import sleep, time
from padtransf import warpPerspectivePadded, warpAffinePadded

import numpy as np
from cv2 import cv2
from matplotlib import pyplot as plt

monitor = {"top": 65, "left": 1705, "width": 850, "height": 465}  # this skips over difficulty/area, if game name/pass already hidden
center_x = int(monitor["width"] / 2)
center_y = int(monitor["height"] / 2)


def map_capture():
    """Gets 3 captures of the map:
        1. Before map displayed
        2. Map displayed (tab pressed)
        3. Map displayed a few frames later (tab still pressed)

    Tab is then depressed. The purpose for the third grab is to filter out any animations, later.
    """
    with mss.mss() as sct:
        # Before map is shown
        pre = sct.grab(monitor)
        keyboard.press_and_release("tab")
        sleep(.075)

        # Map is shown
        during_1 = sct.grab(monitor)
        sleep(.075)

        # Map is still there, but we can tell if any carvers/flames are underneath fucking up the diff
        during_2 = sct.grab(monitor)
        keyboard.press_and_release("tab")
        return pre, during_1, during_2


def map_diff(pre, during_1, during_2):
    """Takes the 3 stages of map capture and outputs a final diff, removing carvers and such"""
    # do first diff

    # do second diff

    # and both diffs together keeping only what's in both
    pass


def map_get_features(diff):
    # sift = cv2.SIFT_create()
    # surf = cv2.SURF

    # Fast style?
    # fast = cv2.FastFeatureDetector_create()
    # fast.setNonmaxSuppression(0)
    # kp = fast.detect(img, None)
    # features = cv2.drawKeypoints(img, kp, None, color=(255, 0, 0))

    # ORB style?
    # orb = cv2.ORB_create()
    orb = cv2.ORB_create(nfeatures=3000, edgeThreshold=0, scoreType=cv2.ORB_FAST_SCORE)
    # orb = cv2.ORB_create(nfeatures=1500, edgeThreshold=0, scoreType=cv2.ORB_FAST_SCORE)
    keypoints, descriptors = orb.detectAndCompute(diff, None)
    # features = cv2.drawKeypoints(diff, keypoints, None, color=(255, 0, 0))

    # Debug showing features
    # cv2.imshow('Features', features)
    # cv2.waitKey(0)

    return keypoints, descriptors


def map_merge_features(diff_1, diff_2):
    keypoints_1, descriptors_1 = map_get_features(diff_1)
    keypoints_2, descriptors_2 = map_get_features(diff_2)

    # Debug showing keypoints
    # cv2.imshow("Result", cv2.drawKeypoints(diff_1, keypoints_1, None, color=(255, 0, 0)))
    # cv2.waitKey(0)
    # cv2.imshow("Result", cv2.drawKeypoints(diff_2, keypoints_2, None, color=(255, 0, 0)))
    # cv2.waitKey(0)

    # Match descriptors between images
    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
    matches = bf.match(descriptors_1, descriptors_2)

    # Debug outputting first 10 matches sorted by dist
    # matches = sorted(matches, key=lambda x: x.distance)
    # img3 = cv2.drawMatches(diff_1, keypoints_1, diff_2, keypoints_2, matches[:10], None, flags=2)
    # cv2.imshow("Result", img3)
    # cv2.waitKey(0)

    # Before merging images together .. make black  alpha? TODO: does this do _anything_ useful?
    diff_1 = cv2.cvtColor(diff_1, cv2.COLOR_BGR2BGRA)
    diff_2 = cv2.cvtColor(diff_2, cv2.COLOR_BGR2BGRA)

    # Extract location of good matches (wtf are good matches?!)
    points1 = np.zeros((len(matches), 2), dtype=np.float32)
    points2 = np.zeros((len(matches), 2), dtype=np.float32)

    for i, match in enumerate(matches):
        points1[i, :] = keypoints_1[match.queryIdx].pt
        points2[i, :] = keypoints_2[match.trainIdx].pt

    # This works...
    H, mask = cv2.estimateAffine2D(points2, points1)
    # H, mask = cv2.estimateAffinePartial2D(points1, points2)  # ??? don't think we need this? doesn't seem to work
    original_with_padding, new_with_padding = warpAffinePadded(diff_2, diff_1, H, flags=cv2.INTER_NEAREST)

    # Let's find red starting point, which may be overwritten by waypoints/other things
    # so we can highlight over it again later
    red_starting_point_mask = np.all(original_with_padding == [0, 0, 255, 255], axis=-1)

    # Merge original with new
    map = cv2.bitwise_or(original_with_padding, new_with_padding)

    # Re-add red mask so it's super clear
    map[red_starting_point_mask] = [0, 0, 255, 255]

    # Debug showing final map!!!
    # cv2.imshow("Result", map)
    # cv2.waitKey(0)
    return map


def map_process():
    """"""
    pass





if __name__ == "__main__":
    images = []
    map = None
    # diff_files = glob("captures/*-difference*.png")
    # print("\n".join(diff_files))


    # diff_1 = cv2.imread("captures/0-difference-map.png")
    # diff_2 = cv2.imread("captures/1-difference-map.png")
    # diff_3 = cv2.imread("captures/2-difference-map.png")
    # diff_4 = cv2.imread("captures/3-difference-map.png")
    #
    # map = map_merge_features(diff_1, diff_2)
    # map = map_merge_features(map, diff_3)
    # map = map_merge_features(map, diff_4)

    counter = 0
    try:
        while True:
            if counter == 0:
                map = cv2.imread(f"captures/{counter}-difference-map.png")

            diff = cv2.imread(f"captures/{counter + 1}-difference-map.png")

            images.append(map)

            start = time()
            map = map_merge_features(map, diff)

            counter += 1
            print(f"Capture {counter} processing: Took {(time() - start) * 1000}ms")

            # Debug showing final map!!!
            cv2.imshow("Result", map)
            cv2.waitKey(0)


    except:
        pass  # lazy exit on file read error









    # for diff in diffs:
    #
    #
    #     cv2.imshow('Result', map)
    #     cv2.waitKey(0)

