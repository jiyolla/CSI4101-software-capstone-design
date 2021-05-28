import threading
import socketserver
import argparse
import time
import pickle
import sys
import os
sys.path.append(os.path.join(sys.path[0], '..'))

from common import serverstate


# Cannot drop outdated server yet
# DRL also doesn't support change in #servers, #models


server_states = {}
num_servers = 2

def empty_states():
    states = {}
    for i in range(num_servers):
        state = serverstate.ServerState(0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
        states[i] = state
    return states

def report_to_drl(pipe_to_drl):
    while True:
        time.sleep(0.1)
        if len(server_states) == num_servers:
            pipe_to_drl.send(server_states)


def recvall(s, message_size):
    fragments = []
    while message_size > 0:
        chunk = s.recv(message_size)
        if not chunk:
            return False
        fragments.append(chunk)
        message_size -= len(chunk)
    return b''.join(fragments)


class Handler(socketserver.BaseRequestHandler):
    # This part should be moved to load_balancer.py

    def handle(self):
        # Should update global variable 'server_states'
        # Instead of just pring raw tegratats
        reporting = True
        while reporting:
            try:
                message_size = int.from_bytes(recvall(self.request, 4), 'big')
                server_state = pickle.loads(recvall(self.request, message_size))
            except TypeError:
                reporting = False
                break
            with threading.Lock():
                server_states[server_state.server_id] = server_state


class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    """Handle requests in a separate thread."""


def run(addr, port, pipe_to_drl):
    if pipe_to_drl is not None:
        report_thread = threading.Thread(target=report_to_drl, args=(pipe_to_drl, ))
        report_thread.start()
    server_address = (addr, port)
    server = ThreadedTCPServer(server_address, Handler)
    print(f'Starting servermonitor server on {addr}:{port}')
    server.serve_forever()


def main(pipe_to_drl=None):
    parser = argparse.ArgumentParser(description='Listen for server state report')
    parser.add_argument(
        '-l',
        '--listen',
        default='localhost',
        help='Specify the IP address on which the server listens',
    )
    parser.add_argument(
        '-p',
        '--port',
        type=int,
        default=8002,
        help='Specify the port on which the server listens',
    )
    args = parser.parse_args()
    run(args.listen, args.port, pipe_to_drl)


if __name__ == '__main__':
    main()
