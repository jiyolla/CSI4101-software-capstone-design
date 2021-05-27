from multiprocessing import Process, Pipe
import loadbalancer
import servermonitor
import evaluater
import time
import threading
import serverstate
import request
from collections import deque


# Currently cannot adatp to change in #server/#model


class DRL:
    def __init__(self, pipe_to_loadbalancer, pipe_to_servermonitor, pipe_to_evaluater):
        # Hpyerparemeter settings
        self.batch_size = 100
        self.observation_interval = 0.1

        self.request_queue = deque()
        self.server_states = {}
        self.pipe_to_loadbalancer = pipe_to_loadbalancer
        self.pipe_to_servermonitor = pipe_to_servermonitor
        self.pipe_to_evaluater = pipe_to_evaluater

    def reward_function(result):
        if sum(result) == 2:
            reward = 100
        elif sum(result) == 1:
            reward = 30
        else:
            reward = -20
        return reward

    def run_and_train(self):
        while True:
            prev_state = serverstate.ServerState.empty_state()
            prev_action = None
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
                state = req_state + svr_state
                # print(state)
                # action = model.predict(state) + some randomness

                # Get reward from evaluater
                reward = 0
                if self.pipe_to_evaluater.poll():
                    reward = reward_function(self.pipe_to_evaluater.recv())
                # print(reward)

                # memory.append(prev_state, prev_action, state, reward)
                #prev_state = state
                #prev_acton = action
            # start a thread to batch training a new model
            # replace current model with new model upon completion


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
