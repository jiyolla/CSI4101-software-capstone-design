import json
import random
import argparse
from multiprocessing import Pipe, Process

from requestgenerator import gen_req
import evaluator


def load_config():
    with open('client.config', 'r') as f:
        config = json.load(f)
        load_balancer_addr = config['load_balancer_addr']
        remote_evaluator_addr = config['remote_evaluator_addr']
        req_per_min = config['req_per_min']
        req_func = config['req_func']
    return req_func, req_per_min, load_balancer_addr, remote_evaluator_addr


def get_config_from_cli():
    load_balancer_addr = f'http://{input("Load balancer ip address: ")}:{input("Load balancer port: ")}'
    remote_evaluator_addr = f'http://{input("Remote Evaluator ip address: ")}:{input("Remote Evaluator port: ")}'
    req_per_min = int(input('Number of requests per minute: '))
    # Currently only 'uniform' is implemented
    req_func = 'uniform'  # eval(input('Request function: '))
    return req_func, req_per_min, load_balancer_addr, remote_evaluator_addr


def get_config_from_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--configure', help='Configure through interactive interface', action='store_true')
    parser.add_argument('-t', '--testcase', help='Generate test case with determined seed=4101', action='store_true')
    args = parser.parse_args()

    if args.testcase:
        random.seed(4101)

    if args.configure:
        return get_config_from_cli()
    else:
        return load_config()


def main():
    req_func, req_per_min, load_balancer_addr, remote_evaluator_addr = get_config_from_args()

    pipe_req_gen_eval, pipe_eval_req_gen = Pipe()
    p_evaluator = Process(target=evaluator.main, args=(remote_evaluator_addr, pipe_eval_req_gen))
    p_evaluator.start()

    gen_req(req_func, req_per_min, load_balancer_addr, pipe_req_gen_eval)


if __name__ == "__main__":
    main()
