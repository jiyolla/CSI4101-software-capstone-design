import json
import pickle
import random
import traceback
import concurrent.futures
import time
import argparse
import sys
import os
sys.path.append(os.path.join(sys.path[0], '..'))

import tensorflow as tf
import numpy as np
import requests

from common import request


# Introduce extra delay by (delay * request size in MB)secs
# Larger value indicate worser connection
region_delay = {
    0: {0: 0, 1: 0.5, 2: 1},
    1: {0: 0.5, 1: 0, 2: 0.75},
    2: {0: 1, 1: 0.75, 2: 0},
}


def send_request(req, load_balancer_addr, evaluater_addr):
    try:
        # 1. Send request meta-data to load balancer to get serving server address
        print(f'Initiating request#{req.unique_id}...')
        data = pickle.dumps(req)
        res = requests.post(load_balancer_addr, data=data)
        server = json.loads(res.text)
        if 'Denied' in server:
            print(f'Request#{req.unique_id} is denied')
            requests.post(evaluater_addr, data=pickle.dumps(server))
            return
        req.set_allocated(server)
        print(f'Request#{req.unique_id} is to be handled by {server}')

        # 2. Send actual request to serving server
        # Pre-processing. This should be moved to server side.
        # Preprocessed data is about 30x larger.
        model = eval(f'tf.keras.applications.{server["model"]}')
        model_group = eval(f'tf.keras.applications.{model._keras_api_names[0].split(".")[2]}')
        h, w = map(int, model.__doc__.split('input_shape: ')[1].split('`(')[1].split(',')[:2])
        img = tf.keras.preprocessing.image.load_img(req.image_path, target_size=[h, w])
        x = tf.keras.preprocessing.image.img_to_array(img)
        x = model_group.preprocess_input(x[tf.newaxis, ...])
        data = json.dumps({"signature_name": "serving_default", "instances": x.tolist()})
        headers = {"content-type": "application/json"}
        req.set_preprocessed()

        json_response = requests.post(f'http://{server["address"]}/v1/models/{server["model"]}:predict', data=data, headers=headers)
        predictions = json.loads(json_response.text)

        # Introduce artifical network overhead here
        time.sleep(region_delay[req.region][server['region']] * len(data)/10**6/2)
        req.set_served(model_group.decode_predictions(np.array(predictions["predictions"]))[0][0][0])

        # Send result to evaluater
        data = pickle.dumps(req)
        requests.post(evaluater_addr, data=data)
        print(f'Request#{req.unique_id} is served.')
    except Exception as err:
        traceback.print_tb(err.__traceback__)
        print(err)


def uniform_request(load_balancer_addr, evaluater_addr, num_req_per_min):
    interval = 60 / num_req_per_min
    end_of_last_request = time.perf_counter_ns()
    with concurrent.futures.ThreadPoolExecutor() as executor:
        req_id = 0
        while True:
            req_id += 1
            start_of_current_request = time.perf_counter_ns()
            time_elapsed = (start_of_current_request - end_of_last_request) / 10**9
            if time_elapsed < interval:
                time.sleep(interval - time_elapsed)

            region = random.randrange(len(region_delay))
            image_id = f'ILSVRC2012_val_{str(random.randint(1, 1000)).zfill(8)}'
            expected_accuracy = random.uniform(0.5, 1)
            expected_time = random.uniform(1, 10)
            req = request.Request(req_id, region, image_id, expected_accuracy, expected_time)
            executor.submit(send_request, req, load_balancer_addr, evaluater_addr)
            end_of_last_request = time.perf_counter_ns()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--configure', help='Configure through interactive interface', action='store_true')
    args = parser.parse_args()

    load_balancer_addr = 'http://35.202.25.144:8000'
    evaluater_addr = 'http://35.202.25.144:8001'
    num_req_per_min = 120
    req_func = uniform_request
    if args.configure:
        load_balancer_addr = f'http://{input("Load balancer ip address: ")}:{input("Load balancer port: ")}'
        evaluater_addr = f'http://{input("Evaluater ip address: ")}:{input("Evaluater port: ")}'
        num_req_per_min = int(input('Number of requests: '))
        # req_func = eval(input('Request function: '))
    req_func(load_balancer_addr, evaluater_addr, num_req_per_min)


if __name__ == "__main__":
    main()
