# coding=utf-8
# ocr 模型训练
import config, os, json, cv2
import tensorflow as tf
import ocr_data_load, ocr_image_split
from tensorflow import keras
from time import sleep
# from ocr_model import SampledSoftmaxModel

idx2char_file  = os.path.join(config.get_root_path(), 'ocr_datas', 'charset.json')

def build_and_train_crnn_model(img_width, img_height):
    """
    模型训练
    :return:
    """
    model_file = os.path.join(config.model_path(), "ocr_model.keras")
    if os.path.exists(model_file):
        if input("模型文件已存在，是否加载(Y)").strip() == 'Y':
            model = keras.models.load_model(model_file)
            if input('模型已加载，是否直接使用(Y)').strip() == 'Y':
                return model

    # 加载图片
    dataset, total_count, num_classes = ocr_data_load.load_label_file()
    split_index = int(0.8 * total_count)
    train_ds = dataset.take(split_index).shuffle(1000).repeat().batch(32).prefetch(tf.data.AUTOTUNE)
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

        keras.layers.Conv2D(256, 3, padding="same", activation="relu"),
        keras.layers.BatchNormalization(),
        keras.layers.GlobalAveragePooling2D(),

        keras.layers.Dense(512, activation='relu'),
        keras.layers.Dropout(0.68),
        keras.layers.Dense(num_classes, activation='softmax')
    ])
    # model = SampledSoftmaxModel(num_classes = num_classes)
    print(model.summary())

    print('model.compile')
    # 使用预热策略
    adam = keras.optimizers.Adam(learning_rate=1e-4)
    model.compile( optimizer=adam, loss="sparse_categorical_crossentropy", metrics=['accuracy'])

    print('model.fit')
    if input('是否开始训练(Y)').strip() != 'Y':
        return
    steps_per_epochs = split_index // 32
    early_stop = keras.callbacks.EarlyStopping(
            monitor="val_accuracy",
            patience = 2,
            restore_best_weights=True,
            verbose=1)
    model.fit(train_ds, validation_data = val_ds, epochs=20, 
              steps_per_epoch = steps_per_epochs, validation_steps = (total_count - split_index) // 32,
              callbacks=[early_stop])

    if input('是否保存模型(Y)').strip() != 'Y':
        return model

    print('model.save')
    if os.path.exists(model_file):
        os.remove(model_file)
    model.save(model_file)

    print('model.end')
    return model

def predict_model(model, size):
    with open(idx2char_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    while True:
        image_path = input('请输入图片地址(q to exit): \n').strip()
        if image_path == 'q':
            break
        if not os.path.exists(image_path):
            print('图片不存在')
            continue
        results = []
        char_imgs = ocr_image_split.segment_characters(image_path, size)
        for image in char_imgs:
            label = model.predict(image)
            label = tf.argmax(label, axis=1).numpy()[0]
            ch = data[str(label)]
            print(f'label: {label}, char: {ch}')
            results.append(ch)
        print(f'charsets: {''.join(results)}')

sleep(1)
size = config.ocr_img_size()
ocr_model = build_and_train_crnn_model(size, size)
if ocr_model is not None:
    # 不为空，开始识别
    predict_model(ocr_model, size)
