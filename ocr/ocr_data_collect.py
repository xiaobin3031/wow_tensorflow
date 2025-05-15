#! /usr/bin/python3.12

import os, config, openpyxl, shutil, random
from PIL import Image, ImageDraw, ImageFont,ImageFilter

cur_dir = os.path.dirname(__file__)
font = ImageFont.truetype(os.path.join(cur_dir, 'SourceHanSerifSC-Light.otf'), 20)
image_path = os.path.join(config.get_root_path(), 'ocr_datas', 'images')
if os.path.exists(image_path):
    shutil.rmtree(image_path)
os.makedirs(image_path, exist_ok=True)
charset_file = os.path.join(config.get_root_path(), 'ocr_datas', 'charset.txt')

samples_per_char = 20

def load_ori_datas():
    """
    加载原始数据，从网上下载文件excel，并且把每个文字都生成一个图片
    :return:
    """
    filename = os.path.join(config.get_root_path(), 'Chinese character list from 2.5 billion words corpus ordered by frequency.xlsx')
    if not os.path.exists(filename):
        return

    workbook = openpyxl.load_workbook(filename=filename)
    sheet = workbook[workbook.sheetnames[0]]
    print(f'sheet name {workbook.sheetnames}')
    # 把数据拆分成训练数据和验证数据
    charsets = []
    for row in sheet.iter_rows(min_row=2, min_col=2, max_col=2):
        for cell in row:
            if cell.value is not None:
                create_image(cell.value, charsets)

    with open(charset_file, 'w+') as w_file:
        for ch in charsets:
            w_file.write(ch + '\n')

def generate_char_image(ch):
    """
    根据文字创建图片，png
    :param ch 文字
    """
    size = config.ocr_img_size()
    image = Image.new('L', (size, size), color=255)
    draw = ImageDraw.Draw(image)
    # 字体 bbox 尺寸
    bbox = draw.textbbox((0, 0), ch, font=font)
    w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
    # 随机居中偏移
    dx = random.randint(-2, 2)
    dy = random.randint(-2, 2)
    x = (size - w) / 2 + dx
    y = (size - h) / 2 + dy
    draw.text((x, y), ch, font=font, fill='black')

    # 可选：轻度模糊 / 旋转
    if random.random() < 0.2:
        image = image.filter(ImageFilter.GaussianBlur(radius=0.5))

    return image


def create_image(ch, charsets):
    """
    根据文字创建图片，png
    :param ch 文字
    """
    for i in range(samples_per_char):
        img = generate_char_image(ch)
        filename = f"{ch}_{i}.png"
        path = os.path.join(image_path, filename)
        img.save(path)
        charsets.append(f"{filename}\t{ch}")

print(os.path.basename(__file__))
load_ori_datas()
