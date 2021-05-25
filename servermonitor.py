import socket
import threading
import socketserver
import json


server_states = {}


def recvall(s, message_size):
    fragments = []
    while message_size > 0:
        chunk = s.recv(message_size)
        if not chunk:
            return False
        fragments.append(chunk)
        message_size -= len(chunk)
    return b''.join(fragments)


class ServerMonitorHandler(socketserver.BaseRequestHandler):
    # This part should be moved to load_balancer.py

    def handle(self):
        # Should update global variable 'server_states'
        # Instead of just pring raw tegratats
        reporting = True
        while reporting:
            try:
                message_size = int.from_bytes(recvall(self.request, 4), 'big')
                server_state = json.loads(recvall(self.request, message_size))
            except TypeError:
                reporting = False
                break
            print(server_state)
            with threading.Lock():
                server_states[server_state['serving_address']] = server_state


class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    pass


if __name__ == "__main__":
    addr_server_monitor = ('', 8002)

    server_monitor_server = ThreadedTCPServer(addr_server_monitor, ServerMonitorHandler)
    with server_monitor_server:
        thread_server_monitor = threading.Thread(target=server_monitor_server.serve_forever)
        thread_server_monitor.daemon = True
        thread_server_monitor.start()
        print("Server loop running in thread:", thread_server_monitor.name)
        thread_server_monitor.join()