import subprocess
import socket
import time
import serverstate
import argparse
import pickle


def run(load, configure):
    """
    if load:
        try:
            with open(input('Type path to config file: '), 'rb') as f:
                server_state = pickle.load(f)
        except OSError:
            print('Failed to load config file')
    if configure:
    """

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        # Hardcoded
        server_address = 'localhost', 8002
        s.connect(server_address)

        # Collect server state info
        server_id = 0
        region = 0
        name = 'jetson_nano_1'
        ip = '222.111.222.238'
        port = '8501'
        models = ''
        available_cpu = None
        available_gpu = None
        available_mem = None
        network_usage = None
        # server_state = serverstate.ServerState(region, name, ip, port, models, available_cpu, available_gpu, available_mem, network_usage)

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
            # server_state['network'] = dict(zip(['in', 'out'], list(map(float, ifstat))))
            network_usage = sum(list(map(float, ifstat)))
            #tegrastats = p_tegrastats.stdout.readline().split()
            #server_state['RAM'] = tegrastats[1].decode()
            #server_state['CPU'] = tegrastats[9].decode()
            #server_state['GPU'] = tegrastats[13].decode()
            server_state = serverstate.ServerState(server_id, region, name, ip, port, models, available_cpu, available_gpu, available_mem, network_usage)
            data = pickle.dumps(server_state)

            # Custom protocle: [4 bytes for data size] + [data]
            s.sendall(len(data).to_bytes(4, 'big'))
            s.sendall(data)


def main():
    parser = argparse.ArgumentParser(description='Collect and report system information')
    parser.add_argument(
        '-l',
        '--load',
        action='store_true',
        help='Load config file',
    )
    parser.add_argument(
        '-c',
        '--configure',
        action='store_true',
        help='Configure through interactive interface',
    )
    args = parser.parse_args()
    run(args.load, args.configure)


if __name__ == '__main__':
    main()