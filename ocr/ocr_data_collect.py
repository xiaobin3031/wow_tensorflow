#! /usr/bin/python3.12

import os, config, openpyxl, shutil, random, threading
from PIL import Image, ImageDraw, ImageFont,ImageFilter

cur_dir = os.path.dirname(__file__)
image_path = os.path.join(config.get_root_path(), 'ocr_datas', 'images')
if os.path.exists(image_path):
    if input('目录已经在，是否清空目录?(Y)').strip() == 'Y':
        print(f'begin clear {image_path}')
        shutil.rmtree(image_path)
        print(f'clear {image_path} success')
os.makedirs(image_path, exist_ok=True)
charset_file = os.path.join(config.get_root_path(), 'ocr_datas', 'charset.txt')

samples_per_char = 20
samples_chars = None
samples_thread_count = 20

def load_fonts():
    font_path = os.path.join(cur_dir, 'fonts')
    fonts = []
    for f_file in os.listdir(font_path):
        font = ImageFont.truetype(os.path.join(font_path, f_file), 20)
        fonts.append(font)
    return fonts

fonts = load_fonts()

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
    chars = []
    for row in sheet.iter_rows(min_row=2, min_col=2, max_col=2):
        for cell in row:
            if cell.value is not None:
                chars.append(cell.value)
    chars = chars[:3000]
    if samples_chars is None or samples_chars >= len(chars):
        total = len(chars)
        # 使用多线程生成
        per_count = total // samples_thread_count
        if total % samples_thread_count > 0:
            per_count = per_count + 1
        threads = []
        for i in range(per_count):
            sub_chars = chars[i * per_count : min((i + 1) * per_count, total)]
            t = threading.Thread(target = thread_create_image, args=(sub_chars, i))
            threads.append(t)
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        """created = 0
        for ch in chars:
            create_image(ch, charsets)
            created = created + 1
            print(f'create: ({created} / {total})')
        """
    else:
        # 随机选择几个
        count = 0
        select_index = []
        created = 0
        total = len(samples_chars)
        while(count < samples_chars):
            index = random.randint(0, len(chars))
            if index in select_index:
                continue
            create_image(chars[index], charsets)
            count = count+ 1
            print(f'create: ({created} / {total})')


    with open(charset_file, 'w+') as w_file:
        for ch in charsets:
            w_file.write(ch + '\n')

def image_change(image, size):
    # 可选：轻度模糊 / 旋转
    if random.random() < 0.5:
        image = image.filter(ImageFilter.GaussianBlur(radius=0.2))

    # 旋转
    if random.random() < 0.5:
        angle = random.randint(-30, 30)
        image = image.rotate(angle, expand=True, fillcolor=255)

    # 缩放
    if random.random() < 0.2:
        if random.random() < 0.5:
            image = image.resize((int(size / 0.67), int(size / 0.67)), resample = Image.Resampling.LANCZOS)
        else:
            image = image.resize((size * 2, size * 2), resample = Image.Resampling.LANCZOS)

    return image

def generate_char_image(ch, font, transform=True):
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

    if transform:
        image = image_change(image, size)

    return image

def thread_create_image(chars, i):
    charsets = []

    for index in range(len(chars)):
        create_image(chars[index], charsets)
        print(f'thread-{i}, create image: {index+1} / {len(chars)}')

    return charsets
def create_image(ch, charsets):
    """
    根据文字创建图片，png
    :param ch 文字
    """
    max_count = samples_per_char * len(fonts)
    for i in range(max_count):
        for font in fonts:
            filename = f"{ch}_{i}.png"
            path = os.path.join(image_path, filename)
            if os.path.exists(path):
                continue
            img = generate_char_image(ch, font)
            img.save(path)
            charsets.append(f"{filename}\t{ch}")

print(os.path.basename(__file__))
load_ori_datas()
