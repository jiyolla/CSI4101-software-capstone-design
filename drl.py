from multiprocessing import Process, Pipe
import loadbalancer
import servermonitor
import evaluater
import time
import threading


class DRL:
    def __init__(self, pipe_to_loadbalancer, pipe_to_servermonitor, pipe_to_evaluater):
        # Hpyerparemeter settings
        self.batch_size = 100
        self.observation_interval = 0.1
        pass
    
        self.pipe_to_loadbalancer = pipe_to_loadbalancer
        self.pipe_to_servermonitor = pipe_to_servermonitor
        self.pipe_to_evaluater = pipe_to_evaluater


    def reward_function(results):
        reward = 0
        for result in results:
            if sum(result) == 2:
                reward += 100
            elif sum(result) == 1:
                reward += 30
            else:
                reward += -20
        return reward


    def run_and_train():
        while True:
        prev_state
        prev_action
        for _ in range(self.batch_size):
            time.sleep(self.observation_interval)
            # If no request in queue
            if self.pipe_to_loadbalancer.poll():
                req
            # action fixed to do nothing
            if not request_queue:
                state = servermonitor.server_states + no request
                action = nothing
            else:
                state = servermonitor.server_states + request_queue.popleft()
                action = model.predict(state) + some randomness
                
            # Get reward from evaluater
            reward = 0
            if pipe_to_evaluater.poll():
                reward = reward_function(self.pipe_to_evaluater.recv())

            memory.append(prev_state, prev_action, state, reward)
            prev_state = state
            prev_acton = action
        start a thread to batch training a new model
        replace current model with new model upon completion


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


if __name__ == '__main__':
    main()
