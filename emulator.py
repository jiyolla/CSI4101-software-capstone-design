# TBD
# 1. Client Request Handler
#     image handling very messy
#     currently just redirect to a single specific jetson server
#     should generate request to DRL server and listen for actions
# 2. Service Server Monitoring
#     currently default polling by tegrastat
#     adjust polling interval
#     struture tegrastat data for drl server feed-in
# 3. Socket to send drl server request
# 4. Socket to receive action
#     Parse action into branches

from tensorflow import keras
import tensorflow as tf
import requests
import socket
import threading
import socketserver
import numpy as np
from PIL import Image
import io
import pickle
import json


def recvall(socket):
    fragments = []
    while True:
        chunk = socket.recv(1024)
        if not chunk:
            break
        fragments.append(chunk)
    return b''.join(fragments)
        

class ClientRequestHandler(socketserver.BaseRequestHandler):

    def handle(self):
        data = recvall(self.request)
        
        # A custom protocol
        # [4 bytes indicating image size] + [image] + [meta-info]
        image_header_size = 4
        # First 4 bytes as the image size
        image_size = int.from_bytes(data[:image_header_size], 'big')
        # Load image
        image = data[image_header_size:image_size + image_header_size]
        # Load meta-info
        meta_info = pickle.loads(data[image_size + image_header_size:])

        # file = keras.utils.get_file('g.jpg', 'https://storage.googleapis.com/download.tensorflow.org/example_images/grace_hopper.jpg')
        # img = keras.preprocessing.image.load_img(file, target_size=[224, 224])
        img = Image.open(io.BytesIO(image)).resize((224, 224))
        x = keras.preprocessing.image.img_to_array(img)
        x = keras.applications.mobilenet.preprocess_input(x[tf.newaxis, ...])
        data = json.dumps({"signature_name": "serving_default", "instances": x.tolist()})
        headers = {"content-type": "application/json"}
        my_jetsonnano_address = '222.111.222.238:8501'
        json_response = requests.post('http://' + my_jetsonnano_address + '/v1/models/img_clf/versions/2:predict', data=data, headers=headers)
        predictions = json.loads(json_response.text)
        print(keras.applications.mobilenet.decode_predictions(np.array(predictions['predictions'])))


class ServerMonitorHandler(socketserver.BaseRequestHandler):

    def handle(self):
        while True:
            data = self.request.recv(1024)
            if not data:
                break
            print(f'received: {data}')


class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    pass

if __name__ == "__main__":
    addr_client_req = ('', 64000)
    addr_server_monitor = ('', 64001)

    client_req_server = ThreadedTCPServer(addr_client_req, ClientRequestHandler)
    server_monitor_server = ThreadedTCPServer(addr_server_monitor, ServerMonitorHandler)
    with client_req_server, server_monitor_server:
        # Start a thread with the server -- that thread will then start one
        # more thread for each request
        thread_client_req = threading.Thread(target=client_req_server.serve_forever)
        # Exit the server thread when the main thread terminates
        thread_client_req.daemon = True
        thread_client_req.start()
        print("Server loop running in thread:", thread_client_req.name)
        
        thread_server_monitor = threading.Thread(target=server_monitor_server.serve_forever)
        thread_server_monitor.daemon = True
        thread_server_monitor.start()
        print("Server loop running in thread:", thread_server_monitor.name)


        # 그냥 막아 일단 ㅋㅋㅋ
        thread_client_req.join()
        client_req_server.shutdown()
        server_monitor_server.shutdown()