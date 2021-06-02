from multiprocessing import Process, Pipe
from collections import deque
import time
import random
import traceback
import json
import sys
import os
sys.path.append(os.path.join(sys.path[0], '..'))

import numpy as np

from common import serverstate, request, available_models
import loadbalancer
import servermonitor
import evaluater

# Currently cannot adatp to change in #server/#model


class RandomPolicy:
    def __init__(self, pipe_to_loadbalancer, pipe_to_servermonitor, pipe_to_evaluater):
        self.num_servers = servermonitor.num_servers
        self.num_models_per_server = len(available_models.lst)
        self.request_queue = deque()
        self.action_space = self.num_models_per_server * self.num_servers + 1
        self.state_space = 4 + 5 * self.num_servers
        self.pipe_to_loadbalancer = pipe_to_loadbalancer
        self.pipe_to_servermonitor = pipe_to_servermonitor
        self.pipe_to_evaluater = pipe_to_evaluater

    def prepare_server(self):
        if self.pipe_to_servermonitor.poll():
            self.server_states = self.pipe_to_servermonitor.recv()
        while self.server_states is None or len(self.server_states) < self.num_servers:
            print('Servers not ready.')
            print('Retrying after 5 seconds...')
            time.sleep(5)
            while self.pipe_to_servermonitor.poll():
                # Exhaust the pipe since we are 5 secs late now
                self.server_states = self.pipe_to_servermonitor.recv()
        print('Servers ready.')
        self.action_to_service = [json.dumps({'Denied': ''}).encode('utf8')]  # action 0 map to service denial
        for server_state in self.server_states.values():
            for model in server_state.models:
                service = {
                    'region': server_state.region,
                    'address': server_state.address,
                    'model': model
                }
                self.action_to_service.append(json.dumps(service).encode('utf8'))

    def return_service_address(self, req_id, action):
        self.pipe_to_loadbalancer.send((req_id, self.action_to_service[action]))

    def log_episode(self, e, episode_reward):
        with open(f'{sys.path[0]}/drl.log', 'a') as f:
            f.write(f'Episode#{e} ended with reward: {episode_reward}')
            f.write(f'Number of all requests: {self.count_all}')
            f.write(f'Number of requests served in time: {self.count_timely}')
            f.write(f'Number of requests served correctly: {self.count_correct}')
            f.write(f'Number of requests denied: {self.count_denial}')

            print(f'Episode#{e} ended with reward: {episode_reward}')
            print(f'Number of all requests: {self.count_all}')
            print(f'Number of requests served in time: {self.count_timely}')
            print(f'Number of requests served correctly: {self.count_correct}')
            print(f'Number of requests denied: {self.count_denial}')

    def reset_req_counters(self):
        self.count_all = 0
        self.count_timely = 0
        self.count_correct = 0
        self.count_denial = 0

    def serve(self):
        try:
            self.prepare_server()
            while True:
                # Read from loadbalancer.py
                # if self.pipe_to_loadbalancer.poll():
                self.request_queue.append(self.pipe_to_loadbalancer.recv())

                if self.request_queue:
                    req = self.request_queue.popleft()
                    req_id = req.unique_id
                    action = random.randrange(1, self.action_space)
                    self.return_service_address(req_id, action)

        except Exception as err:
            traceback.print_tb(err.__traceback__)
            print(err)

    def run(self):
        p_serve = Process(target=self.serve)
        p_serve.start()


def main():
    pipe_to_loadbalancer, pipe_from_loadbalancer = Pipe()
    pipe_to_servermonitor, pipe_from_servermonitor = Pipe()
    pipe_to_evaluater, pipe_from_evaluater = Pipe()

    p_loadbalancer = Process(target=loadbalancer.main, args=(pipe_from_loadbalancer, ))
    p_servermonitor = Process(target=servermonitor.main, args=(pipe_from_servermonitor, ))
    p_evaluater = Process(target=evaluater.main, args=(pipe_from_evaluater, ))
    p_loadbalancer.start()
    p_servermonitor.start()
    p_evaluater.start()

    rp = RandomPolicy(pipe_to_loadbalancer, pipe_to_servermonitor, pipe_to_evaluater)
    rp.run()


if __name__ == '__main__':
    main()
