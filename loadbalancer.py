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
import numpy as np
import requests
import socket
import threading
import socketserver
from PIL import Image
import io
import pickle
import json
from datetime import datetime
import evaluater


server_states = []


def recvall(s):
    fragments = []
    while True:
        chunk = s.recv(1024)
        if not chunk:
            break
        fragments.append(chunk)
    return b''.join(fragments)


class ClientRequestHandler(socketserver.BaseRequestHandler):
    # Return the serving and model.

    def handle(self):
        request = pickle.loads(recvall(self.request))
        print(request)
        
        # Some DRL decision
        pass
    
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.send
    


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