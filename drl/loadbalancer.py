from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
import argparse
import pickle
import threading


class Communicator:
    def __init__(self):
        self.answers = {}

    def set_pipe(self, pipe_to_drl):
        self.pipe_to_drl = pipe_to_drl

    def queries_to_drl(self, req):
        self.pipe_to_drl.send(req)

    def answer_from_drl(self, req_id):
        while True:
            if req_id in self.answers:
                with threading.Lock():
                    return self.answers.pop(req_id)
            if self.pipe_to_drl.poll():
                answer = self.pipe_to_drl.recv()
                with threading.Lock():
                    self.answers[answer[0]] = answer[1]


c = Communicator()


class Handler(BaseHTTPRequestHandler):

    def do_POST(self):
        req = pickle.loads(self.rfile.read(int(self.headers['Content-Length'])))

        # Make DRL decision with req
        global c
        c.queries_to_drl(req)
        server = c.answer_from_drl(req.unique_id)
        print(server)

        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(server)
        """
        self.wfile.write(json.dumps({
            'region': 0,
            'address': '222.111.222.238:8501',
            'model': 'MobileNet'
        }).encode('utf8)')
        """


def run(addr, port, pipe_to_drl):
    c.set_pipe(pipe_to_drl)
    server_address = (addr, port)
    server = ThreadingHTTPServer(server_address, Handler)
    print(f'Starting loadbalancer server on {addr}:{port}')
    server.serve_forever()


def main(pipe_to_drl=None):
    parser = argparse.ArgumentParser(description='Listen for client request for server resolving')
    parser.add_argument(
        '-l',
        '--listen',
        default='',
        help='Specify the IP address on which the server listens',
    )
    parser.add_argument(
        '-p',
        '--port',
        type=int,
        default=8000,
        help='Specify the port on which the server listens',
    )
    args = parser.parse_args()
    run(args.listen, args.port, pipe_to_drl)


if __name__ == '__main__':
    main()
