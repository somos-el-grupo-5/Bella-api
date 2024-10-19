# pylint: skip-file
import numpy as np
import os
from PIL import Image, ImageColor
import cv2
from app.utils.image_utils import lips, evaluate

def process_image_logic(img_file, lip_color_hex):
    lip_color = ImageColor.getcolor(lip_color_hex, "RGB")
    image = np.array(Image.open(img_file))
    ori = image.copy()
    h, w, _ = ori.shape
    image = cv2.resize(image, (1024, 1024))
    
    cp = os.path.join(os.path.dirname(__file__), '../cp/79999_iter.pth')
    parsing = evaluate(img_file, cp)
    parsing = cv2.resize(parsing, image.shape[0:2], interpolation=cv2.INTER_NEAREST)

    part = 12  # Labio superior
    image = lips(image, parsing, part, lip_color)
    
    part = 13  # Labio inferior
    image = lips(image, parsing, part, lip_color)
    
    image = cv2.resize(image, (w, h))
    return Image.fromarray(image)