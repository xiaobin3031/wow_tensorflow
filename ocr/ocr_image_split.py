import cv2
import numpy as np
from PIL import Image

def preprocess_image(image_path):
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    _, thresh = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    return thresh

def segment_characters(thresh_img, re_size):
    projection = np.sum(thresh_img, axis=0)   # 垂直投影
    in_char = False
    start, end = 0, 0
    char_regions = []

    for i, val in enumerate(projection):
        if val > 0 and not in_char:
            in_char = True
            start = i
        elif val == 0 and in_char:
            in_char = False
            end = i
            char_regions.append((start, end))

    chars = []
    for (start, end) in char_regions:
        char_img = thresh_img[:, start: end]
        char_img = cv2.resize(char_img, (size, size)).astype(np.float32) / 255.0
        char_img = np.expand_dims(char_img, axis=(0, -1)) # shape: (1, H, W 1)
        chars.append(char_img)

    return chars
