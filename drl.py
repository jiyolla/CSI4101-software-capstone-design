from multiprocessing import Process, Pipe
import servermonitor
import evaluater
import time
from collections import deque
import threading






class DRL:
    def __init__(self):
        # hpyerparemeter settings
        self.request_queue = deque()
        self.hi = 0
        self.request_counter = 0
        
    def query(self, request):
        with threading.Lock():
            self.request_counter += 1
            self.request_queue.append((self.request_counter, request))


def main():
    pipe_to_loadbalancer, pipe_from_loadbalancer = Pipe()
    pipe_to_servermonitor, pipe_from_servermonitor = Pipe()
    pipe_to_evaluater, pipe_from_evaluater = Pipe()

    p_loadbalancer = Process(target=loadbalancer.main, args=(pipe_from_loadbalancer, ))
    p_servermonitor = Process(target=servermonitor.main, args=(pipe_from_servermonitor, ))
    p_evaluater = Process(target=evaluater.main, args=(pipe_from_evaluater, ))
    p.start()
    while True:
        time.sleep(0.1)
        if parent_conn.poll():
            print(parent_conn.recv())
        else:
            print('hi')
    """
        servermonitor.main()
        while True:
            prev_state
            prev_action
            for _ in range(batch_size):
                # make an observeation every 0.1 seconds
                time.sleep(0.1)
                # If no request in queue
                # action fixed to do nothing
                if not request_queue:
                    state = servermonitor.server_states + no request
                    action = nothing
                else:
                    state = servermonitor.server_states + request_queue.popleft()
                    action = model.predict(state) + some randomness


                memory.append(prev_state, prev_action, state, reward)
            start a thread to batch training a new model
            replace current model with new model upon completion
    """


if __name__ == '__main__':
    main()
