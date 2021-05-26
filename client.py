from tensorflow import keras
import tensorflow as tf
import numpy as np
import json
import pickle
import random
import concurrent.futures
import requests
import time
import request # our own definition
# import argparse

# Introduce extra delay by (delay * request size in MB)secs
# Larger value indicate worser connection
region_delay = {
    0: {0: 0, 1: 0.5, 2: 1},
    1: {0: 0.5, 1:0, 2: 0.75},
    2: {0: 1, 1: 0.75, 2: 0}
}


def send_request(req, load_balancer_addr, evaluater_addr):
    # 1. Send request meta-data to load balancer to get serving server address
    data = pickle.dumps(req)
    res = requests.post(load_balancer_addr, data=data)
    server = json.loads(res.text)
    req.set_allocated(server)

    # 2. Send actual request to serving server

    # Pre-processing. This should be moved to server side.
    # Preprocessed data is about 30x larger.
    img = keras.preprocessing.image.load_img(req.image_path, target_size=[224, 224])
    x = keras.preprocessing.image.img_to_array(img)
    x = keras.applications.mobilenet.preprocess_input(x[tf.newaxis, ...])
    data = json.dumps({"signature_name": "serving_default", "instances": x.tolist()})
    headers = {"content-type": "application/json"}
    req.set_preprocessed()

    json_response = requests.post(f'http://{server["address"]}/v1/models/{server["model"]}:predict', data=data, headers=headers)
    predictions = json.loads(json_response.text)

    # Introduce artifical network overhead here
    time.sleep(region_delay[req.region][server['region']] * len(data)/10*6)
    req.set_served(keras.applications.densenet.decode_predictions(np.array(predictions['predictions']))[0][0][0])

    data = pickle.dumps(req)
    requests.post(evaluater_addr, data=data)

    return request


def main():
    # parser = argparse.ArgumentParser()
    # parser.add_argument('-t', '--test', help='Perform local test', action='store_true')
    # args = parser.parse_args()

    num_req = 3

    with concurrent.futures.ThreadPoolExecutor(max_workers=num_req) as executor:
        load_balancer_addr = 'http://localhost:8000'
        evaluater_addr = 'http://localhost:8001'
        threads = []
        for _ in range(num_req):
            region = random.randrange(3)
            image_id = f'ILSVRC2012_val_{str(random.randint(1, 100)).zfill(8)}'
            accuracy = random.uniform(0.5, 1)
            time = random.randint(1, 10)
            req = request.Request(region, image_id, accuracy, time)
            threads.append(executor.submit(send_request, req, load_balancer_addr, evaluater_addr))


if __name__ == "__main__":
    main()
