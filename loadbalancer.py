import argparse
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import pickle


class S(BaseHTTPRequestHandler):
    def do_POST(self):
        req = pickle.loads(self.rfile.read(int(self.headers['Content-Length'])))

        # Make DRL decision with req
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps({
            'region': 0,
            'address': '222.111.222.238:8501',
            'model': 'MobileNet',
            'model_group': 'mobilenet'
        }).encode('utf8)'))


def run(addr, port, server_class=HTTPServer, handler_class=S):
    server_address = (addr, port)
    httpd = server_class(server_address, handler_class)

    print(f"Starting httpd server on {addr}:{port}")
    httpd.serve_forever()


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Run a simple HTTP server")
    parser.add_argument(
        "-l",
        "--listen",
        default="localhost",
        help="Specify the IP address on which the server listens",
    )
    parser.add_argument(
        "-p",
        "--port",
        type=int,
        default=8000,
        help="Specify the port on which the server listens",
    )
    args = parser.parse_args()
    run(addr=args.listen, port=args.port)
