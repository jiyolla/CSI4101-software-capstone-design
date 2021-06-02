from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
import argparse
import pickle
import sys
import os
import traceback

import pandas as pd


df = pd.read_csv(os.path.join(sys.path[0], '../data/LOC_val_solution.csv'))


class Communicator:
    def __init__(self):
        self.answers = {}

    def set_pipe(self, pipe_to_drl):
        self.pipe_to_drl = pipe_to_drl

    def report_to_drl(self, result):
        self.pipe_to_drl.send(result)


c = Communicator()


class Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            global c
            req = pickle.loads(self.rfile.read(int(self.headers['Content-Length'])))

            self.send_response(200)
            self.send_header('Content-type', 'text')
            self.end_headers()
            if isinstance(req, dict) and 'Denied' in req:
                print(f'A request is denied')
                c.report_to_drl(req)
                return

            # Give reward to DRL based on req and its res
            print_to_stdout = []
            print_to_stdout.append('-'*80)
            print_to_stdout.append(f'Request region: {req.region}')
            print_to_stdout.append(f'Served region: {req.served_by["region"]}')
            print_to_stdout.append(f'Served model: {req.served_by["model"]}\n')

            # Time requirement
            is_timely = req.elapsed_time <= req.expected_time
            print_to_stdout.append(f'Elapsed time: {req.elapsed_time}')
            print_to_stdout.append(f'Expected time: {req.expected_time}')
            print_to_stdout.append(f'is_timely: {is_timely}\n')

            # Accuracy requirement
            is_correct = req.response in df[df['ImageId'] == req.image_id]['PredictionString'].to_string()
            print_to_stdout.append(f'Image Id: {req.image_id}')
            print_to_stdout.append(f'Ground truth: {df[df["ImageId"] == req.image_id]["PredictionString"].to_string(index=False)}')
            print_to_stdout.append(f'Prediction: {req.response}')
            print_to_stdout.append(f'is_correct: {is_correct}\n')
            print_to_stdout.append('-'*80)
            print('\n'.join(print_to_stdout))

            c.report_to_drl((is_timely, is_correct))
        except Exception as err:
            traceback.print_tb(err.__traceback__)
            print(err)

    def log_message(self, *args):
        """Silence logging"""


def run(addr, port, pipe_to_drl):
    c.set_pipe(pipe_to_drl)
    server_address = (addr, port)
    server = ThreadingHTTPServer(server_address, Handler)
    print(f'Starting evaluater server on {addr}:{port}')
    server.serve_forever()


def main(pipe_to_drl=None):
    parser = argparse.ArgumentParser(description='Listen for response result')
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
        default=8001,
        help='Specify the port on which the server listens',
    )
    args = parser.parse_args()
    run(args.listen, args.port, pipe_to_drl)


if __name__ == '__main__':
    main()
