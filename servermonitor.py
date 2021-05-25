import socket
import threading
import socketserver


server_states = []

class ServerMonitorHandler(socketserver.BaseRequestHandler):
    # This part should be moved to load_balancer.py

    def handle(self):
        # Should update global variable 'server_states'
        # Instead of just pring raw tegratats
        reporting = True
        while reporting:
            fragments = []
            message_size = 5
            while message_size > 0:
                data = self.request.recv(message_size)
                if not data:
                    reporting = False
                    break
                else:
                    fragments.append(data)
                    message_size -= len(data)
            print(f'received: {b"".join(fragments)}')


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

        # 그냥 막아 일단 ㅋㅋㅋ
        thread_server_monitor.join()
        server_monitor_server.shutdown()