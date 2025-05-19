# coding=utf-8

import config, os, json, cv2
import tensorflow as tf
import numpy as np

ocr_data_dir = os.path.join(config.get_root_path(), 'ocr_datas')
size = config.ocr_img_size()

def decode_image(filename, label):
    image = tf.io.read_file(filename)
    image = tf.image.decode_png(image, channels=1)
    image = tf.image.convert_image_dtype(image, tf.float32)
    image = tf.image.resize(image, [size, size])
    return image, label

def load_label_file():
    filenames = []
    labels = []
    charset = set()
    image_path = os.path.join(ocr_data_dir, 'images')
    label_file = os.path.join(ocr_data_dir, 'charset.txt')
    idx2char_file = os.path.join(ocr_data_dir, 'charset.json')

    with open(label_file, 'r', encoding='utf-8') as f:
        for line in f:
            filename, char = line.strip().split('\t')
            filenames.append(os.path.join(image_path, filename))
            labels.append(char)
            charset.add(char)

    charset = sorted(list(charset))
    char2idx = {ch: i for i, ch in enumerate(charset)}
    label_indices = [char2idx[ch] for ch in labels]

    dataset = tf.data.Dataset.from_tensor_slices((filenames, label_indices))
    dataset = dataset.map(decode_image).shuffle(buffer_size = 10000)
    
    idx2char = {i: ch for ch, i in char2idx.items()}
    with open(idx2char_file, 'w', encoding='utf-8') as f:
        json.dump(idx2char, f, ensure_ascii=False)

    return dataset, len(filenames), len(charset)

if __name__ == '__main__':
    load_label_file()
