from multiprocessing import Process, Pipe, Queue
from collections import deque
import time
import threading
import random
import sys
import os
sys.path.append(os.path.join(sys.path[0], '..'))

import tensorflow as tf
import numpy as np

from common import serverstate, request
import loadbalancer
import servermonitor
import evaluater

# Currently cannot adatp to change in #server/#model


class DRL:
    def __init__(self, pipe_to_loadbalancer, pipe_to_servermonitor, pipe_to_evaluater):
        # Hpyerparemeter settings
        self.batch_size = 100
        self.observation_interval = 0.1
        self.explore_chance = 0.7
        self.final_explore_chance = 0.01
        self.explore_chance_decay = 0.995
        self.discount_factor = 0.99

        self.num_servers = 2
        self.num_models_per_server = 8
        self.request_queue = deque()
        self.memory = []
        self.server_states = servermonitor.empty_states()
        self.action_space = self.num_models_per_server * self.num_servers + 1
        self.state_space = 4 + 5 * self.num_servers
        self.pipe_to_loadbalancer = pipe_to_loadbalancer
        self.pipe_to_servermonitor = pipe_to_servermonitor
        self.pipe_to_evaluater = pipe_to_evaluater

    def build_model(self):
        model = tf.keras.models.Sequential()
        model.add(tf.keras.layers.Dense(units=64, activation='relu', input_dim=self.state_space))
        model.add(tf.keras.layers.Dense(units=32, activation='relu'))
        model.add(tf.keras.layers.Dense(units=self.state_space, activation='linear'))
        model.compile(loss=tf.keras.losses.Huber(), optimizer=tf.keras.optimizers.Adam())
        return model

    def reward_function(result):
        if sum(result) == 2:
            reward = 100
        elif sum(result) == 1:
            reward = 30
        else:
            reward = -20
        return reward

    def batch_train(self, model, ret):
        batch = self.memory[:self.batch_size]
        with threading.Lock():
            self.memory = self.memory[self.batch_size:]

        X = []
        Y = []
        for state, action, next_state, reward in batch:
            reward = reward + self.discount_factor * np.amax(model.predict(next_state)[0])
            target = self.model.predict(state)[0]
            target[action] = reward
            X.append(state)
            Y.append(target)
        X = np.array(X)
        Y = np.array(Y)
        model.fit(X, Y, epochs=1, verbose=0)
        ret.put(model)

    def run_and_train(self):
        model = self.build_model()
        new_model = None
        p_train = None
        ret = Queue()
        while True:
            prev_state = serverstate.ServerState.empty_state()
            prev_action = 0
            for _ in range(self.batch_size):
                time.sleep(self.observation_interval)

                # Read from servermonitor.py
                if self.pipe_to_servermonitor.poll():
                    self.server_states = self.pipe_to_servermonitor.recv()

                # Read from loadbalancer.py
                if self.pipe_to_loadbalancer.poll():
                    self.request_queue.append(self.pipe_to_loadbalancer.recv())

                # If no request is present
                # action fixed to do nothing
                if not self.request_queue:
                    req_state = request.Request.empty_state()
                else:
                    req_state = self.request_queue.popleft().to_state()
                svr_state = [state_el for server_state in self.server_states.values() for state_el in server_state.to_state()]
                state = np.array([req_state + svr_state])
                print(state)

                if random.random() < self.explore_chance:
                    action = random.randrange(self.action_space)
                else:
                    action = np.amax(model.predict(state)[0])
                self.explore_chance *= self.explore_chance_decay

                # Get reward from evaluater
                reward = 0
                if self.pipe_to_evaluater.poll():
                    reward = self.reward_function(self.pipe_to_evaluater.recv())
                # print(reward)

                with threading.Lock():
                    self.memory.append((prev_state, prev_action, state, reward))
                prev_state = state
                prev_action = action

            # start a thread to batch training a new model
            # replace current model with new model upon completion
            if p_train is not None:
                model = ret.get()
                p_train.join()
            new_model = model
            p_train = Process(target=self.batch_train, args=(new_model, ret))
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
    drl.run_and_train()


if __name__ == '__main__':
    main()
