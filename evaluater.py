import argparse
from http.server import HTTPServer, BaseHTTPRequestHandler
import pandas as pd
import pickle
import request

df = pd.read_csv('data/LOC_val_solution.csv')


class S(BaseHTTPRequestHandler):
    def do_POST(self):
        req = pickle.loads(self.rfile.read(int(self.headers['Content-Length'])))

        self.send_response(200)

        # Give reward to DRL based on req and its res
        print('-'*80)
        print(f'Request region: {req.region}')
        print(f'Served region: {req.served_by["region"]}')
        print(f'Served model: {req.served_by["model"]}\n')

        # Time requirement
        is_timely = req.elapsed_time <= req.expected_time
        print(f'Elapsed time: {req.elapsed_time}')
        print(f'Expected time: {req.expected_time}')
        print(f'is_timely: {is_timely}\n')

        # Accuracy requirement
        is_correct = req.response in df[df['ImageId'] == req.image_id]['PredictionString'].to_string()
        print(f'Image Id: {req.image_id}')
        print(f'Ground truth: {df[df["ImageId"] == req.image_id]["PredictionString"].to_string(index=False)}')
        print(f'Prediction: {req.response}')
        print(f'is_correct: {is_correct}\n')

        return is_timely, is_correct


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
        default=8001,
        help="Specify the port on which the server listens",
    )
    args = parser.parse_args()
    run(addr=args.listen, port=args.port)
