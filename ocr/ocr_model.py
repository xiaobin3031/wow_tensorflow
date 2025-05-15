# coding=utf-8
# ocr 模型训练
import config, os
import tensorflow as tf
import ocr_data_load
from tensorflow import keras
from time import sleep

def build_and_train_crnn_model(img_width, img_height):
    """
    模型训练
    :return:
    """
    model_file = "ocr_model.h5"
    if os.path.exists(model_file):
        use_old_model = input("模型文件已存在，是否直接使用(Y)").strip()
        if use_old_model == 'Y':
            return keras.models.load_model(model_file)

    # 加载图片
    dataset, total_count, num_classes = ocr_data_load.load_label_file()
    split_index = int(0.8 * total_count)
    train_ds = dataset.take(split_index).shuffle(buffer_size=split_index, reshuffle_each_iteration=True).repeat().batch(32).prefetch(tf.data.AUTOTUNE)
    val_ds = dataset.skip(split_index).batch(32).prefetch(tf.data.AUTOTUNE)

    print('model.init')
    model = keras.Sequential([
        keras.Input(shape=(img_height, img_width, 1)),

        keras.layers.Conv2D(32, 3, activation='relu', padding="same"),
        keras.layers.BatchNormalization(),
        keras.layers.MaxPooling2D(),

        keras.layers.Conv2D(64, 3, activation='relu', padding="same"),
        keras.layers.BatchNormalization(),
        keras.layers.MaxPooling2D(),

        keras.layers.Conv2D(128, 3, padding="same", activation="relu"),
        keras.layers.BatchNormalization(),
        keras.layers.GlobalAveragePooling2D(),

        keras.layers.Dense(256, activation=tf.nn.relu),
        keras.layers.Dropout(0.5),
        keras.layers.Dense(num_classes, activation=tf.nn.softmax)
    ])
    print(model.summary())

    print('model.compile')
    model.compile(optimizer="adam", loss="sparse_categorical_crossentropy", metrics=['accuracy'])

    print('model.fit')
    to_train = input('是否开始训练(Y)').strip()
    if to_train != 'Y':
        return
    steps_per_epochs = split_index // 32
    model.fit(train_ds, validation_data = val_ds, epochs=100, 
              steps_per_epoch = steps_per_epochs, validation_steps = (total_count - split_index) // 32)

    save_model = input('是否保存模型(Y)').strip()
    if save_model != 'Y':
        return

    print('model.save')
    if os.path.exists(model_file):
        os.remove(model_file)
    model.save(model_file)

    print('model.end')
    return model

sleep(1)
size = config.ocr_img_size()
build_and_train_crnn_model(size, size)
