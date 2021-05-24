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
from datetime import datetime
import evaluater


server_states = []

def recvall(socket):
    fragments = []
    while True:
        chunk = socket.recv(1024)
        if not chunk:
            break
        fragments.append(chunk)
    return b''.join(fragments)


class ClientRequestHandler(socketserver.BaseRequestHandler):
    # Some part of this code should be moved to load_balancer.py
    # The emulation part stays

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
        meta_info['timestamps']['accepted'] = datetime.now()
        
        print(meta_info)

        # Send meta_info and server states to DRL
        # askDRL(meta_info, server_states)
        pass

        # ClientRequestHandler ENDS here
        # Receiving DRL's response/action could be done in other section
        # Codes below just show that jetson-nano is working
        # Should be moved into other parts
        example_drl_response = {
            'service_address': '222.111.222.238:8501',
            'service_model': 'MobileNet'
        }
        
        # Preprocessing. It should be moved to serving server.
        # MODIFY the pretrained keras models to include the preprocessing.
        # img = keras.preprocessing.image.load_img(file_path, target_size=[224, 224])
        img = Image.open(io.BytesIO(image)).resize((224, 224))
        x = keras.preprocessing.image.img_to_array(img)
        x = keras.applications.mobilenet.preprocess_input(x[tf.newaxis, ...])
        data = json.dumps({"signature_name": "serving_default", "instances": x.tolist()})
        
        # Actual request. It should either be moved to client side or load balancer side.
        # If load balancer is an edge server then it's probably ok to make actual request in load balancer
        headers = {"content-type": "application/json"}
        json_response = requests.post('http://' + example_drl_response['service_address']
                                      + '/v1/models/'
                                      + example_drl_response['service_model']
                                      + ':predict', data=data, headers=headers)
        predictions = json.loads(json_response.text)
        meta_info['timestamps']['served'] = datetime.now()
        # For debugging
        print(keras.applications.mobilenet.decode_predictions(np.array(predictions['predictions'])))

        meta_info['timestamps']['served'] = datetime.now()
        response = keras.applications.densenet.decode_predictions(np.array(predictions['predictions']))[0][0][0]
        
        # call evaluater to rate the response
        is_timely, is_success = evaluater.evaluate(meta_info, response)

        # feed back to DRL
        pass


class ServerMonitorHandler(socketserver.BaseRequestHandler):
    # This part should be moved to load_balancer.py

    def handle(self):
        # Should update global variable 'server_states'
        # Instead of just pring raw tegratats
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