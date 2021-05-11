# TBD
# 1. Read Training Data
#     1)Dataset ready - tiny-imagenet-200(
#     2)Load training data and add id to request
# 2. Generate Request
#     Currently very messy image sending. Need fix.
#     Sophiscated and Controlled periodic generation. 

import socket
import json
import base64


if __name__ == "__main__":
    file = 'test.jpg'
    with open(file, 'rb') as f:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            my_goorm_addr = ('3.36.64.61', 56472)
            # ip, port = 'localhost', 64000
            # sock.connect((ip, port))
            sock.connect(my_goorm_addr)

            message = {'image': base64.encodebytes(f.read()).decode('utf-8'), 'accuracy': 90, 'time': 3}
            message = json.dumps(message)

            sock.sendall(bytes(message, encoding='utf-8'))