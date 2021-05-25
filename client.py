from tensorflow import keras
import tensorflow as tf
import numpy as np
import json
import pickle
import random
import concurrent.futures
import requests
import request # our own definition
# import argparse


def send_request(req, load_balancer_addr, evaluater_addr):
    # 1. Send request meta-data to load balancer to get serving server address
    data = pickle.dumps(req)
    res = requests.post(load_balancer_addr, data=data)
    server = json.loads(res.text)
    req.set_allocated(server)

    # 2. Send actual request to serving server

    # Pre-processing based on the model.
    # Maybe it should be done the server side. There are pros and cons.

    # Should be modfied to adapt to the model
    img = keras.preprocessing.image.load_img(req.image_path, target_size=[224, 224])
    x = keras.preprocessing.image.img_to_array(img)
    x = keras.applications.mobilenet.preprocess_input(x[tf.newaxis, ...])
    data = json.dumps({"signature_name": "serving_default", "instances": x.tolist()})
    headers = {"content-type": "application/json"}
    req.set_preprocessed()

    json_response = requests.post(f'http://{server["address"]}/v1/models/{server["model"]}:predict', data=data, headers=headers)
    predictions = json.loads(json_response.text)
    req.set_served(keras.applications.densenet.decode_predictions(np.array(predictions['predictions']))[0][0][0])
    
    data = pickle.dumps(req)
    requests.post(evaluater_addr, data=data)

    return request


def main():
    # parser = argparse.ArgumentParser()
    # parser.add_argument('-t', '--test', help='Perform local test', action='store_true')
    # args = parser.parse_args()

    num_req = 10

    with concurrent.futures.ThreadPoolExecutor(max_workers=num_req) as executor:
        load_balancer_addr = 'http://localhost:8000'
        evaluater_addr = 'http://localhost:8001'
        threads = []
        for _ in range(num_req):
            region = random.randrange(5)
            image_id = f'ILSVRC2012_val_{str(random.randint(1, 100)).zfill(8)}'
            accuracy = random.uniform(0.5, 1)
            time = random.randint(1, 10)
            req = request.Request(region, image_id, accuracy, time)
            threads.append(executor.submit(send_request, req, load_balancer_addr, evaluater_addr))

        for future in concurrent.futures.as_completed(threads):
            print(future.result())


if __name__ == "__main__":
    main()
