# TBD
# 1. Read Training Data
#     1)Dataset ready - ILSVRC2012 validation dataset
#     2)Load training data and add id to request
#     3)Probably make the meta_info a class for better abstraction
# 2. Generate Request
#     Sophiscated and Controlled periodic generation

import socket
import pickle
from datetime import datetime, timedelta
import random
import concurrent.futures
# import argparse


class Client:
    def __init__(self, region):
        self.region = region


class Request:
    def __init__(self, image_path, accuracy, time):
        self.image_path = image_path
        self.accuracy = accuracy
        self.time = time


def generate_request(client, request):
    with open(request.image_path, 'rb') as f:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            server_address = 'localhost', 64000
            # server_address = '', 0
            s.connect(server_address)

            image = f.read()
            meta_info = {
                'image_id': request.image_path[-28:-5],
                'image_size': len(image),
                'requirement': {
                    'accuracy': request.accuracy,
                    'time': request.time
                },
                'timestamps': {
                    'created': datetime.now(),
                    'accepted': None,
                    'served': None
                },
                'initial_server': 0
            }

            # A custom protocol
            # [4 bytes indicating image size] + [image] + [meta-info]
            s.sendall(len(image).to_bytes(4, 'big'))
            s.sendall(image)
            s.sendall(pickle.dumps(meta_info))


def main():
    # parser = argparse.ArgumentParser()
    # parser.add_argument('-t', '--test', help='Perform local test', action='store_true')
    # args = parser.parse_args()

    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        for _ in range(3):
            region = random.randrange(5)
            client = Client(region)

            image_number = random.randint(1, 100)
            image_path = f'data/image/ILSVRC2012_val_{str(image_number).zfill(8)}.JPEG'
            accuracy = random.uniform(0.5, 1)
            time = timedelta(seconds=random.randint(1, 10))
            request = Request(image_path, accuracy, time)

            future = executor.submit(generate_request, client, request)
            print(future.result())


if __name__ == "__main__":
    main()
