from time import sleep

import keyboard
import mouse
import mss
import numpy as np
from PIL import Image
from cv2 import cv2



def outline_hovered_item(image):
    # templar_coat = cv2.cvtColor(templar_coat, cv2.COLOR_BGRA2BGR)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # find the box..

    # Debug: Image read ok?
    # cv2.imshow("Templar coat", templar_coat)
    # cv2.waitKey(0)
    # cv2.imshow("Templar coat", gray)
    # cv2.waitKey(0)

    # # thresh_inv = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
    # thresh_inv = cv2.threshold(gray, 125, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
    # blur = cv2.GaussianBlur(thresh_inv, (1, 1), 0)
    # # blur = cv2.GaussianBlur(blur, (1, 1), 0)
    # # blur = cv2.GaussianBlur(blur, (1, 1), 0)
    # thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]


    # Other style, shows ONLY the white text neatly!
    # _, thresh_inv = cv2.threshold(gray, 240, 255, cv2.CHAIN_APPROX_NONE)  # WTF!
    # blur = cv2.GaussianBlur(thresh_inv, (1, 1), 0)
    # thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]


    # other style, relying on preprocessing elsewhere
    thresh = gray



    # thresh = cv2.dilate(thresh, None, iterations=15)
    # thresh = cv2.erode(thresh, None, iterations=3)


    # Debug: Image processing the box nicely?
    # cv2.imshow("Box processing blur", blur)
    # cv2.waitKey(0)
    # cv2.imshow("Box processing thresh", thresh)
    # cv2.waitKey(0)

    # find contours
    # contours = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[0]
    contours = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)[0]

    mask = np.ones(image.shape[:2], dtype="uint8") * 255
    for c in contours:
        # get the bounding rect
        x, y, w, h = cv2.boundingRect(c)
        if w * h > 5000 and (x, y) != (0, 0):
            print((x, y), x + w, y + h)
            cv2.rectangle(mask, (x, y), (x + w, y + h), (0, 0, 255), -1)

    # templar_coat[mask[:,:]] = [0, 0, 255]
    res_final = cv2.bitwise_and(image, image, mask=cv2.bitwise_not(mask))

    cv2.imshow("boxes", mask)
    cv2.imshow("final image", res_final)
    cv2.waitKey(0)
    cv2.destroyAllWindows()



def get_bounds_for_hovered_item_text(image):
    pass



def get_item_text():
    """Be currently hovering over the item.."""
    x, y = mouse.get_position()
    print(f"mouse was at ({x}, {y})")

    # move out of way, capture screen, move back, get diff, that's item!
    with mss.mss() as sct:
        mouse.move(1, 1, duration=.1)
        sleep(.1)

        # Before item is shown
        pre = np.array(sct.grab(sct.monitors[0]))

        mouse.move(x, y, duration=.1)
        sleep(.1)

        # Item is now shown
        post = np.array(sct.grab(sct.monitors[0]))


        # diffing time
        threshold = 0.2
        absdiff = cv2.absdiff(pre, post)
        _, thresholded = cv2.threshold(absdiff, int(threshold * 255), 255, cv2.THRESH_BINARY)

        # cv2.imshow("absdiff", absdiff)
        # cv2.imshow("thresholded", thresholded)
        # cv2.waitKey(0)
        # cv2.destroyAllWindows()

        # outline_hovered_item(thresholded)
        # get_bounds_for_hovered_item_text(thresholded)

        # print("[INFO] loading EAST text detector...")
        # net = cv2.dnn.readNet(args["east"])








        # rgb = cv2.pyrDown(thresholded)
        rgb = thresholded
        small = cv2.cvtColor(rgb, cv2.COLOR_BGR2GRAY)

        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
        grad = cv2.morphologyEx(small, cv2.MORPH_GRADIENT, kernel)

        _, bw = cv2.threshold(grad, 0.0, 255.0, cv2.THRESH_BINARY | cv2.THRESH_OTSU)

        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (17, 5))
        connected = cv2.morphologyEx(bw, cv2.MORPH_CLOSE, kernel)
        # using RETR_EXTERNAL instead of RETR_CCOMP
        contours, hierarchy = cv2.findContours(connected.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        # For opencv 3+ comment the previous line and uncomment the following line
        # _, contours, hierarchy = cv2.findContours(connected.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

        mask = np.zeros(bw.shape, dtype=np.uint8)

        found_rect = None  # should only find 1!

        for idx in range(len(contours)):
            x, y, w, h = cv2.boundingRect(contours[idx])
            mask[y:y + h, x:x + w] = 0
            cv2.drawContours(mask, contours, idx, (255, 255, 255), -1)
            r = float(cv2.countNonZero(mask[y:y + h, x:x + w])) / (w * h)

            if r > 0.45 and w * h > 10_000:
                print(f"Found big old item at ({x}, {y})")
                found_rect = x, y, w, h
                cv2.rectangle(rgb, (x, y), (x + w - 1, y + h - 1), (0, 255, 0), 2)

        text_x, text_y, text_w, text_h = found_rect
        cut_out_text = post[text_y:text_y + text_h, text_x:text_x + text_w]



        from d2vs.ocr import OCR
        ocr = OCR()
        results = ocr.read(cut_out_text, width_ths=2.5)
        for bounds, text, item_type in results:
            print(text)

        cv2.imshow('rects', rgb)
        cv2.imshow('cut out text', cut_out_text)
        cv2.waitKey(0)
        cv2.destroyAllWindows()








if __name__ == "__main__":

    # # this was working
    # # templar_coat = cv2.imread("captures/templar_coat.png")
    # # outline_hovered_item(templar_coat)
    #
    # unearthly_flamberge = cv2.imread("captures/unearthly_flamberge.png")
    # outline_hovered_item(unearthly_flamberge)
    #
    # tal_rashas_lidless_eye = cv2.imread("captures/tal_rashas_lidless_eye.png")
    # outline_hovered_item(tal_rashas_lidless_eye)
    keyboard.add_hotkey("f12", get_item_text)

    while True:
        sleep(.1)
