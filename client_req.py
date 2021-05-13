# TBD
# 1. Read Training Data
#     1)Dataset ready - tiny-imagenet-200(
#     2)Load training data and add id to request
# 2. Generate Request
#     Sophiscated and Controlled periodic generation. 

import socket
import pickle
from datetime import datetime
import argparse


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--test', help='Perform local test', action='store_true')
    args = parser.parse_args()

    image_file_path = 'data/image/ILSVRC2012_val_00000001.JPEG'
    with open(image_file_path, 'rb') as f:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if args.test:
                server_address = 'localhost', 64000
            else:
                # Actual address of the server expected
                server_address = '', 0
            s.connect(server_address)

            image = f.read()
            meta_info = {
                'image_id': image_file_path[-8:],
                'image_size': len(image),
                'requirement': {
                    'accuracy': 90,
                    'time': 3
                },
                'timestamps': {
                    'created': datetime.now()
                }
                'initial_server': 0
            }

            # A custom protocol
            # [4 bytes indicating image size] + [image] + [meta-info]
            s.sendall(len(image).to_bytes(4, 'big'))
            s.sendall(image)
            s.sendall(pickle.dumps(meta_info))


if __name__ == "__main__":
    main()
