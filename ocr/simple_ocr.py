import os
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import tensorflow as tf
from tensorflow.keras import layers, models
import random

cur_dir = os.path.dirname(__file__)
# 中文字符集（可换成你想训练的）
CHARS = ['我', '你', '他', '是', '的', '在', '有', '中', '国', '人']
IMG_SIZE = 32
NUM_SAMPLES_PER_CHAR = 10
font = ImageFont.truetype(os.path.join(cur_dir, 'SourceHanSerifSC-Light.otf'), 20)

# 1. 生成图片数据
def generate_char_image(char, size=IMG_SIZE):
    image = Image.new('L', (size, size), color=255)  # 白底
    draw = ImageDraw.Draw(image)
    draw.text((size / 2, size / 2), char, font=font, fill=0, anchor="mm")
    return np.array(image)

# 2. 构造数据集
def build_dataset():
    X, y = [], []

    for idx, char in enumerate(CHARS):
        for _ in range(NUM_SAMPLES_PER_CHAR):
            img = generate_char_image(char)
            img = img / 255.0  # 归一化
            X.append(img[..., np.newaxis])
            y.append(idx)

    X = np.array(X, dtype=np.float32)
    y = np.array(y, dtype=np.int32)
    return X, y

# 3. 定义模型
def create_model(num_classes):
    model = models.Sequential([
        layers.Input(shape=(IMG_SIZE, IMG_SIZE, 1)),
        layers.Conv2D(32, 3, activation='relu'),
        layers.MaxPooling2D(),
        layers.Conv2D(64, 3, activation='relu'),
        layers.MaxPooling2D(),
        layers.Flatten(),
        layers.Dense(128, activation='relu'),
        layers.Dense(num_classes, activation='softmax')
    ])
    model.compile(optimizer='adam',
                  loss='sparse_categorical_crossentropy',
                  metrics=['accuracy'])
    return model

# 4. 训练 & 测试
X, y = build_dataset()
model = create_model(num_classes=len(CHARS))
model.fit(X, y, epochs=20, batch_size=16, validation_split=0.2)
model.save("ocr_char_model")

# 5. 预测示例
def predict_char(img):
    img = img / 255.0
    pred = model.predict(img[np.newaxis, ..., np.newaxis])
    idx = np.argmax(pred)
    return CHARS[idx]

# 示例预测
sample_img = X[0].squeeze() * 255
Image.fromarray(sample_img.astype(np.uint8)).show()
print("预测为：", predict_char(X[0].squeeze()))
