import subprocess
import socket
import json
import time
import serverstate
import argparse
import pickle


def run(load, configure):
    if load:
        try:
            with open(input('Type path to config file: '), 'rb') as f:
                server_state = pickle.load(f)
        except OSError:
            print('Failed to load config file')
    if configure:
        
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        # server_address = '', 8001
        server_address = 'localhost', 8002
        s.connect(server_address)

        # Collect server state info
        server_state = {
            'server_name': 'my_jetson_nano',
            'serving_address': '222:111:222:238:8501',
            'available_models': 'should be scanned automatically',
        }

        # Network stats using 'ifstat'
        p_ifstat = subprocess.Popen('ifstat', stdout=subprocess.PIPE)
        # p_tegrastats = subprocess.Popen('tegrastats', stdout=subprocess.PIPE)
        # Consume headers
        p_ifstat.stdout.readline()
        p_ifstat.stdout.readline()
        # Read contents
        # for line in iter(p_ifstat.stdout.readline, b''):
        while(True):
            time.sleep(1)
            ifstat = p_ifstat.stdout.readline().split()
            server_state['network'] = dict(zip(['in', 'out'], list(map(float, ifstat))))
            #tegrastats = p_tegrastats.stdout.readline().split()
            #server_state['RAM'] = tegrastats[1].decode()
            #server_state['CPU'] = tegrastats[9].decode()
            #server_state['GPU'] = tegrastats[13].decode()
            data = json.dumps(server_state).encode('utf-8')

            # Custom protocle: [4 bytes for data size] + [data]
            s.sendall(len(data).to_bytes(4, 'big'))
            s.sendall(data)

def main():
    parser = argparse.ArgumentParser(description='Collect and report system information')
    parser.add_argument(
        '-l',
        '--load',
        action=store_true,
        help='Load config file',
    )
    parser.add_argument(
        '-c',
        '--configure',
        action=store_true
        help='Configure through interactive interface',
    )
    args = parser.parse_args()
    run(args.load, args.configure)



if __name__ == '__main__':
    main()