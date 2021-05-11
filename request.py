from tensorflow import keras
import tensorflow as tf
import matplotlib.pyplot as plt
import numpy as np
import random
import json
import requests

file = keras.utils.get_file('g.jpg', 'https://storage.googleapis.com/download.tensorflow.org/example_images/grace_hopper.jpg')
img = keras.preprocessing.image.load_img(file, target_size=[224, 224])
x = keras.preprocessing.image.img_to_array(img)
x = keras.applications.mobilenet.preprocess_input(x[tf.newaxis, ...])


fashion_mnist = keras.datasets.fashion_mnist
(train_images, train_labels), (test_images, test_labels) = fashion_mnist.load_data()

# scale the values to 0.0 to 1.0
test_images = test_images / 255.0

# reshape for feeding into the model
test_images = test_images.reshape(test_images.shape[0], 28, 28, 1)

class_names = ['T-shirt/top', 'Trouser', 'Pullover', 'Dress', 'Coat',
               'Sandal', 'Shirt', 'Sneaker', 'Bag', 'Ankle boot']

print('test_images.shape: {}, of {}'.format(x.shape, x.dtype))

rando = random.randint(0,len(test_images)-1)
show(rando, 'An Example Image: {}'.format(class_names[test_labels[rando]]))

data = json.dumps({"signature_name": "serving_default", "instances": x.tolist()})
print('Data: {} ... {}'.format(data[:50], data[len(data)-52:]))


# send data using POST request and receive prediction result
headers = {"content-type": "application/json"}
json_response = requests.post('http://222.111.222.238:8501/v1/models/img_clf/versions/2:predict', data=data, headers=headers)
predictions = json.loads(json_response.text)

print(keras.applications.mobilenet.decode_predictions(np.array(predictions['predictions'])))
