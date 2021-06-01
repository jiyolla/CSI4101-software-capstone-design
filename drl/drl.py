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


class DRL:
    def __init__(self, pipe_to_loadbalancer, pipe_to_servermonitor, pipe_to_evaluater):
        # Hpyerparemeter settings
        self.observation_interval = 0.25
        self.seconds_per_batch = 10
        self.batch_size = int(self.seconds_per_batch / self.observation_interval)
        self.explore_chance = 0.7
        self.final_explore_chance = 0.01
        self.explore_chance_decay = 0.995
        self.discount_factor = 0.999

        self.num_servers = servermonitor.num_servers
        self.num_models_per_server = len(available_models.lst)
        self.request_queue = deque()
        self.server_states = None
        self.action_space = self.num_models_per_server * self.num_servers + 1
        self.state_space = 4 + 5 * self.num_servers
        self.pipe_to_loadbalancer = pipe_to_loadbalancer
        self.pipe_to_servermonitor = pipe_to_servermonitor
        self.pipe_to_evaluater = pipe_to_evaluater

    def build_model(self, tf):
        model = tf.keras.models.Sequential()
        model.add(tf.keras.layers.Dense(units=64, activation='relu', input_dim=self.state_space))
        model.add(tf.keras.layers.Dense(units=32, activation='relu'))
        model.add(tf.keras.layers.Dense(units=self.state_space, activation='linear'))
        model.compile(loss=tf.keras.losses.Huber(), optimizer=tf.keras.optimizers.Adam())
        return model

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

    def reward_function(result):
        if result is None:
            # big penalty for denying request
            reward = -1000
        elif sum(result) == 2:
            reward = 100
        elif sum(result) == 1:
            reward = 30
        else:
            reward = -20
        return reward

    def serve(self, pipe_to_train):
        try:
            import tensorflow as tf
            model = self.build_model(tf)
            weights = pipe_to_train.recv()
            model.set_weights(weights)
            prev_state = np.array([[0]*self.state_space])
            prev_action = 0
            end_of_last_observation = time.perf_counter_ns()

            self.prepare_server()

            for e in range(1000):
                memory = []
                for t in range(self.batch_size):
                    start_of_current_observation = time.perf_counter_ns()
                    time_elapsed = (start_of_current_observation - end_of_last_observation) / 10**9
                    if time_elapsed < self.observation_interval:
                        time.sleep(self.observation_interval - time_elapsed)

                    # Read from servermonitor.py
                    if self.pipe_to_servermonitor.poll():
                        new_server_states = self.pipe_to_servermonitor.recv()
                        for key, value in new_server_states.items():
                            self.server_states[key] = value
                    if self.server_states is None or len(self.server_states) < self.num_servers:
                        print('Servers not ready.')
                        print('Retrying after 5 seconds...')
                        time.sleep(5)
                        continue

                    # Read from loadbalancer.py
                    if self.pipe_to_loadbalancer.poll():
                        self.request_queue.append(self.pipe_to_loadbalancer.recv())

                    # If no request is present
                    # action fixed to do nothing
                    no_request = False
                    if not self.request_queue:
                        no_request = True
                        req_state = request.Request.empty_state()
                    else:
                        req = self.request_queue.popleft()
                        req_id = req.unique_id
                        req_state = req.to_state()
                    svr_state = [state_el for server_state in self.server_states.values() for state_el in server_state.to_state()]
                    state = np.array([req_state + svr_state])
                    # print(f'{e}-{t}: {state}')

                    if no_request:
                        action = 0
                    else:
                        if random.random() < self.explore_chance:
                            action = random.randrange(self.action_space)
                        else:
                            action = np.argmax(model.predict(state)[0])
                        self.explore_chance *= self.explore_chance_decay
                        self.return_service_address(req_id, action)

                    # Get reward from evaluater
                    reward = 0
                    if self.pipe_to_evaluater.poll():
                        reward = self.reward_function(self.pipe_to_evaluater.recv())
                        print(reward)

                    memory.append((prev_state, prev_action, state, reward))
                    prev_state = state
                    prev_action = action
                    end_of_last_observation = time.perf_counter_ns()

                # start a thread to batch training a new model
                # replace current model with new model upon completion
                print('calling batch_train...')
                pipe_to_train.send(memory[:])
                if pipe_to_train.poll():
                    print('updating model...')
                    weights = pipe_to_train.recv()
                    model.set_weights(weights)
        except Exception as err:
            traceback.print_tb(err.__traceback__)
            print(err)

    def train(self, pipe_to_serve):
        try:
            import tensorflow as tf
            model = self.build_model(tf)
            pipe_to_serve.send(model.get_weights())
            while True:
                # Start batch train upon signal from serve process
                memory = pipe_to_serve.recv()

                X = []
                Y = []
                for state, action, next_state, reward in memory:
                    # print(state, action, next_state, reward)
                    reward = reward + self.discount_factor * np.amax(model.predict(next_state)[0])
                    target = model.predict(state)[0]
                    target[action] = reward
                    X.append(state[0])
                    Y.append(target)
                X = np.array(X)
                Y = np.array(Y)
                # print('start training...')
                model.fit(X, Y, epochs=1)# , verbose=0)
                # print('finish training...')
                pipe_to_serve.send(model.get_weights())
        except Exception as err:
            traceback.print_tb(err.__traceback__)
            print(err)

    def run(self):
        pipe_1, pipe_2 = Pipe()
        p_serve = Process(target=self.serve, args=(pipe_1, ))
        p_train = Process(target=self.train, args=(pipe_2, ))
        p_serve.start()
        p_train.start()


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

    drl = DRL(pipe_to_loadbalancer, pipe_to_servermonitor, pipe_to_evaluater)
    drl.run()


if __name__ == '__main__':
    main()
