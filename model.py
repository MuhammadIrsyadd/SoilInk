# -*- coding: utf-8 -*-
"""model

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1XCD8XGAfSno3WmDTY0HdoMHak4Y4WNEH
"""

from google.colab import drive
drive.mount('/content/drive')

import os
import tensorflow as tf
import tensorflow_hub as hub
from tensorflow.keras.preprocessing.image import ImageDataGenerator, img_to_array, load_img
import cv2
import numpy as np
from PIL import Image
from io import BytesIO
import matplotlib.pylab as plt

# Define the Google Drive path
google_drive_path = '/content/drive/MyDrive/dataset2'
# Ensure the directory exists
os.makedirs(google_drive_path, exist_ok=True)

# Define the training and validation base directories
train_dir = os.path.join(google_drive_path, 'train1')
validation_dir = os.path.join(google_drive_path, 'validation1')
test_dir = os.path.join(google_drive_path, 'test1')

# Mendefinisikan path model MobileNetV2 dari TensorFlow Hub
model_url = "https://tfhub.dev/google/tf2-preview/mobilenet_v2/classification/4"

# Membuat model dengan MobileNetV2 dari TensorFlow Hub
model = tf.keras.Sequential([
    hub.KerasLayer(model_url, input_shape=(224, 224, 3)),
    tf.keras.layers.Dense(64, activation='relu'),
    tf.keras.layers.Dense(32, activation='relu'),
    tf.keras.layers.Dense(16, activation='relu'),
    tf.keras.layers.Dense(8, activation='softmax')  # 8 kelas tanah
])

# Menggunakan ImageDataGenerator untuk augmentasi gambar
datagen = ImageDataGenerator(
    rescale=1./255,
    rotation_range=20,
    shear_range=0.2,
    zoom_range=0.2,
    horizontal_flip=True,
    fill_mode='nearest'
)

# Mendefinisikan generator untuk data latih
train_generator = datagen.flow_from_directory(
    train_dir,  # Ganti dengan path dataset training
    target_size=(224, 224),
    batch_size=32,
    class_mode='categorical'
)

# Mendefinisikan generator untuk data validasi
val_generator = datagen.flow_from_directory(
    validation_dir,  # Ganti dengan path dataset validasi
    target_size=(224, 224),
    batch_size=32,
    class_mode='categorical'
)

# Mendefinisikan generator untuk data pengujian
test_generator = datagen.flow_from_directory(
    test_dir,  # Ganti dengan path dataset pengujian
    target_size=(224, 224),
    batch_size=32,
    class_mode='categorical'
)

# Mengompilasi model
model.compile(optimizer='adam',
              loss='categorical_crossentropy',
              metrics=['accuracy'])

# Melatih model dengan data latih dan validasi
history = model.fit(train_generator, epochs=30, validation_data=val_generator)

# Evaluasi model pada dataset pengujian
test_loss, test_acc = model.evaluate(test_generator)
print(f"Test Accuracy: {test_acc}")

class_names = train_generator.class_indices
print(class_names)

import numpy as np
import matplotlib.pyplot as plt

# Fungsi untuk menampilkan gambar dengan prediksi
def show_images_with_predictions(images, labels, predictions, class_names):
    num_images = len(images)
    num_rows = 5
    num_cols = (num_images + num_rows - 1) // num_rows

    plt.figure(figsize=(15, 3 * num_rows))
    for i in range(num_images):
        plt.subplot(num_rows, num_cols, i + 1)
        plt.imshow(images[i])
        true_label = class_names[np.argmax(labels[i])]
        pred_label = class_names[predictions[i]]
        plt.title(f'True: {true_label}\nPredicted: {pred_label}')
        plt.axis('off')
    plt.show()

# Ambil satu batch gambar dari generator data latih
image_batch, label_batch = next(train_generator)

# Lakukan prediksi menggunakan model
predictions = model.predict(image_batch)
predicted_labels = np.argmax(predictions, axis=1)

# Ambil kelas nama dari generator data latih
class_names = list(train_generator.class_indices.keys())

# Evaluate the model on the test set
test_loss, test_accuracy = model.evaluate(test_generator)
print(f'Test Loss: {test_loss}, Test Accuracy: {test_accuracy}')

# Tampilkan gambar dengan prediksi
show_images_with_predictions(image_batch, label_batch, predicted_labels, class_names)

acc = history.history['accuracy']
val_acc = history.history['val_accuracy']
loss = history.history['loss']
val_loss = history.history['val_loss']

epochs = range(len(acc))

plt.plot(epochs, acc, 'r', label='Training accuracy')
plt.plot(epochs, val_acc, 'b', label='Validation accuracy')
plt.title('Training and validation accuracy')
plt.legend(loc=0)
plt.figure()

plt.plot(epochs, loss, 'r', label='Training Loss')
plt.plot(epochs, val_loss, 'b', label='Validation Loss')
plt.title('Training and validation loss')
plt.legend(loc=0)
plt.figure()

plt.show()

model.summary()

try:
    model.save("/content/drive/MyDrive/dataset2/my_model.h5")
except Exception as e:
    print("Error:", str(e))

import numpy as np
from google.colab import files
from tensorflow.keras.utils import load_img, img_to_array
import tensorflow as tf
import tensorflow_hub as hub
from tensorflow.keras.preprocessing.image import ImageDataGenerator

# Upload the image
uploaded = files.upload()

# Load pre-trained weights
model.load_weights('/content/drive/MyDrive/dataset2/my_model.h5')

# Preprocess the uploaded image and make predictions
for fn in uploaded.keys():
    # Predicting images
    path = '/content/' + fn
    img = load_img(path, target_size=(224, 224))
    x = img_to_array(img)
    x /= 255
    x = np.expand_dims(x, axis=0)

    # Make predictions
    predictions = model.predict(x)
    print(predictions)

    # Get the predicted class
    predicted_class = np.argmax(predictions[0])

    # Assuming labels are from 0 to 7 (adjust accordingly based on your dataset)
    print(fn + " is predicted to belong to class " + str(predicted_class))

"""BATAS MODEL SAMPE SINI KE BAWAHNYA ITU BUAT DEPLOY """

import tensorflow as tf
import tensorflow_hub as hub

# Mendaftarkan KerasLayer sebagai objek kustom
custom_objects = {'KerasLayer': hub.KerasLayer}

# Menggunakan custom_object_scope untuk meregister objek kustom
with tf.keras.utils.custom_object_scope(custom_objects):
    # Load model Keras (.h5)
    model = tf.keras.models.load_model("/content/drive/MyDrive/dataset2/my_model.h5")

    # Convert model ke format TensorFlow Lite
    converter = tf.lite.TFLiteConverter.from_keras_model(model)
    tflite_model = converter.convert()

# Simpan model TensorFlow Lite
with open('my_model.tflite', 'wb') as f:
    f.write(tflite_model)