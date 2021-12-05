import numpy as np
import os
import loaddata
import cv2
from d2vs.ocr import OCR
from PIL import Image


ocr = OCR()
imgfile = Image.open('.\d2vs\Capture.PNG')
img = np.array(imgfile)
img = cv2.cvtColor(img, cv2.COLOR_BGRA2RGB)

cv2.imshow("After BGRA2RGB", img)
cv2.waitKey(0)
cv2.destroyAllWindows()

data = ocr.read(np.asarray(img,dtype='uint8'))

for _,text, item_type in data:
    text = text.lower()
    text = text.strip()
    print(text)
    #text = text.strip()
    print(item_type)

    if "unid" in text:

        print("Item has not been identified.  Lets check to see if we should ID it or throw it.")
        break



