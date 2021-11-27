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

    thresh_inv = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]

    # Blur the image
    blur = cv2.GaussianBlur(thresh_inv, (1, 1), 0)

    thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

    # find contours
    contours = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[0]

    mask = np.ones(image.shape[:2], dtype="uint8") * 255
    for c in contours:
        # get the bounding rect
        x, y, w, h = cv2.boundingRect(c)
        if w * h > 1000 and (x, y) != (0, 0):
            print((x, y), x + w, y + h)
            cv2.rectangle(mask, (x, y), (x + w, y + h), (0, 0, 255), -1)

    # templar_coat[mask[:,:]] = [0, 0, 255]
    res_final = cv2.bitwise_and(image, image, mask=cv2.bitwise_not(mask))

    cv2.imshow("boxes", mask)
    cv2.imshow("final image", res_final)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


if __name__ == "__main__":

    # this was working
    # templar_coat = cv2.imread("captures/templar_coat.png")
    # outline_hovered_item(templar_coat)

    unearthly_flamberge = cv2.imread("captures/unearthly_flamberge.png")
    outline_hovered_item(unearthly_flamberge)

    tal_rashas_lidless_eye = cv2.imread("captures/tal_rashas_lidless_eye.png")
    outline_hovered_item(tal_rashas_lidless_eye)
