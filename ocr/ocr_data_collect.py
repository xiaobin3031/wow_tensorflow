#! /usr/bin/python3.12

import os, config, openpyxl, time
from PIL import Image, ImageDraw, ImageFont

cur_dir = os.path.dirname(__file__)
img_path = os.path.join(config.get_root_path(), 'ocr_datas')
os.makedirs(img_path, exist_ok=True)
font = ImageFont.truetype(os.path.join(cur_dir, 'SourceHanSerifSC-Light.otf'), 30)

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
    for row in sheet.iter_rows(min_row=2, min_col=2, max_col=2):
        for cell in row:
            if cell.value is not None:
                create_image(cell.value)

def create_image(ch):
    """
    根据文字创建图片，png
    :param ch 文字
    """
    width, height = 30, 40
    image = Image.new('RGBA', (width, height), color=(255, 255, 255, 0))
    draw = ImageDraw.Draw(image)
    draw.text((0, 0), ch, font=font, fill=(0, 0, 0))
    image.save(os.path.join(img_path, ch + ".png"))

print(os.path.basename(__file__))
# load_ori_datas()
