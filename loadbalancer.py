from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
import argparse
import json
import pickle
import threading


queries = []
answers = {}


def queries_to_drl(pipe_to_drl):
    while True:
        time.sleep(0.1)
        pipe_to_drl.send(queries)
        with threading.Lock():
            queries = []


def answer_from_drl(req_id):
    while True:
        if req_id in answers:
            return answers.pop(req_id)
        answer = pipe_to_drl.recv()
        answers[answer[0]] = answer[1]
        
    

class Handler(BaseHTTPRequestHandler):

    def do_POST(self):
        req = pickle.loads(self.rfile.read(int(self.headers['Content-Length'])))

        # Make DRL decision with req
        with threading.Lock():
            queries.append(req)
        server = answer_from_drl(req.unique_id)
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({
            'region': 0,
            'address': '222.111.222.238:8501',
            'model': 'MobileNet',
            'model_group': 'mobilenet'
        }).encode('utf8)'))


def run(addr, port, pipe_to_drl):
    if pipe_to_drl is not None:
        report_thread = threading.Thread(target=report_to_drl, args=(pipe_to_drl, ))
        report_thread.start()
    server_address = (addr, port)
    server = ThreadingHTTPServer(server_address, Handler)
    print(f'Starting loadbalancer server on {addr}:{port}')
    server.serve_forever()


def main(pipe_to_drl=None):
    parser = argparse.ArgumentParser(description='Listen for client request for server resolving')
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
        default=8000,
        help='Specify the port on which the server listens',
    )
    args = parser.parse_args()
    run(args.listen, args.port, pipe_to_drl)

if __name__ == '__main__':
    main()
