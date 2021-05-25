# TBD
# 1. Read Training Data
#     1)Dataset ready - ILSVRC2012 validation dataset
#     2)Load training data and add id to request
#     3)Probably make the meta_info a class for better abstraction
# 2. Generate Request
#     Sophiscated and Controlled periodic generation

from tensorflow import keras
import tensorflow as tf
import numpy as np
import json
import pickle
from datetime import datetime, timedelta
import random
import concurrent.futures
import requests
import imagesize
# import argparse


class Request:
    def __init__(self, client_region, image_path, accuracy, time):
        self.image_path = image_path
        self.accuracy = accuracy
        self.time = time
        self.image_size = imagesize.get(image_path)
        self.timestamps = {
            'Created': datetime.now(),
            'Allocated': None,
            'Served': None
        }

    def set_allocated(self):
        self.timestamps['Allocated'] = datetime.now()

    def set_served(self):
        self.timestamps['Served'] = datetime.now()


def send_request(request):
    # 1. Send request meta-data to load balancer to get serving server address
    # 2. Send actual request to serving server
    
    res = requests.get('http://localhost:8000')
    server = json.loads(res.text)
    request.set_allocated()
        
    # Pre-processing based on the model.
    # Maybe it should be done the server side. There are pros and cons.
    
    # Should be modfied to adapt to the model
    img = keras.preprocessing.image.load_img(request.image_path, target_size=[224, 224])
    x = keras.preprocessing.image.img_to_array(img)
    x = keras.applications.mobilenet.preprocess_input(x[tf.newaxis, ...])
    
    
    data = json.dumps({"signature_name": "serving_default", "instances": x.tolist()})
    headers = {"content-type": "application/json"}
    json_response = requests.post(f'http://{server["address"]}/v1/models/{server["model"]}:predict', data=data, headers=headers)
    predictions = json.loads(json_response.text)
    response = keras.applications.densenet.decode_predictions(np.array(predictions['predictions']))#[0][0][0]
    request.set_served()

    return server['region'], response, request


def main():
    # parser = argparse.ArgumentParser()
    # parser.add_argument('-t', '--test', help='Perform local test', action='store_true')
    # args = parser.parse_args()
    
    num_req = 10

    with concurrent.futures.ThreadPoolExecutor(max_workers=num_req) as executor:
        threads = []
        for _ in range(num_req):
            client_region = random.randrange(5)
            image_number = random.randint(1, 100)
            image_path = f'data/image/ILSVRC2012_val_{str(image_number).zfill(8)}.JPEG'
            accuracy = random.uniform(0.5, 1)
            time = timedelta(seconds=random.randint(1, 10))
            request = Request(client_region, image_path, accuracy, time)
            threads.append(executor.submit(send_request, request))

        for future in concurrent.futures.as_completed(threads):
            print(future.result())


if __name__ == "__main__":
    main()
