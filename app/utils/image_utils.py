# pylint: skip-file
import numpy as np
import cv2
from skimage.filters import gaussian
from app.test.test import evaluate

def lips(image, parsing, part=12, color=[230, 50, 20]):
    b, g, r = color
    tar_color = np.zeros_like(image)
    tar_color[:, :, 0] = b
    tar_color[:, :, 1] = g
    tar_color[:, :, 2] = r
    np.repeat(parsing[:, :, np.newaxis], 3, axis=2)

    image_hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    tar_hsv = cv2.cvtColor(tar_color, cv2.COLOR_BGR2HSV)
    image_hsv[:, :, 0:1] = tar_hsv[:, :, 0:1]

    changed = cv2.cvtColor(image_hsv, cv2.COLOR_HSV2BGR)
    changed[parsing != part] = image[parsing != part]
    
    return changed