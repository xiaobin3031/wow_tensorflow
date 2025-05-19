# coding=utf-8
# ocr 模型训练
import tensorflow as tf
from tensorflow import keras

class SampledSoftmaxModel(keras.Model):
    def __init__(self, num_classes, embed_dim=256, **kwargs):
        super().__init__(**kwargs)
        self.feature_extractor = keras.Sequential([
            keras.layers.Conv2D(32, 3, activation='relu', padding="same"),
            keras.layers.BatchNormalization(),
            keras.layers.MaxPooling2D(),

            keras.layers.Conv2D(64, 3, activation='relu', padding="same"),
            keras.layers.BatchNormalization(),
            keras.layers.MaxPooling2D(),

            keras.layers.Conv2D(128, 3, activation='relu', padding="same"),
            keras.layers.BatchNormalization(),
            keras.layers.GlobalAveragePooling2D(),

            keras.layers.Dense(embed_dim, activation='relu'),
            keras.layers.Dropout(0.5),
        ])

        # 重要：分类器权重和偏置
        self.class_weights = self.add_weight(
            name="class_weights",
            shape=[num_classes, embed_dim],
            initializer="glorot_uniform",
            trainable=True
        )
        self.class_bias = self.add_weight(
            name="class_bias",
            shape=[num_classes],
            initializer="zeros",
            trainable=True
        )
        self.num_classes = num_classes
        self.embed_dim = embed_dim

    def call(self, inputs, training=False):
        return self.feature_extractor(inputs, training=training)

    def train_step(self, data):
        images, labels = data

        with tf.GradientTape() as tape:
            embeddings = self(images, training=True)

            loss = tf.reduce_mean(tf.nn.sampled_softmax_loss(
                weights=self.class_weights,
                biases=self.class_bias,
                labels=tf.reshape(labels, [-1, 1]),
                inputs=embeddings,
                num_sampled=self.num_classes // 2,     # 你可以根据类别数量调大
                num_classes=self.num_classes
            ))

        gradients = tape.gradient(loss, self.trainable_variables)
        self.optimizer.apply_gradients(zip(gradients, self.trainable_variables))
        self.compiled_metrics.update_state(labels, tf.argmax(tf.matmul(embeddings, tf.transpose(self.class_weights)) + self.class_bias, axis=-1))

        results = {m.name: m.result() for m in self.metrics}
        results['loss'] = loss
        return results

