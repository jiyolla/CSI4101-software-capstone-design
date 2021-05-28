import subprocess
import socket
import time
import sys
sys.path.append("..")
from common import serverstate
import argparse
import pickle

def run(load, configure, tegrastats_flag):
    """
    if load:
        try:
            with open(input('Type path to config file: '), 'rb') as f:
                server_state = pickle.load(f)
        except OSError:
            print('Failed to load config file')
    """

    # Collect server state info
    server_id = 0
    region = 0
    name = 'jetson_nano_1'
    ip = '222.111.222.238'
    port = '8501'
    models = ''
    available_cpu = 50
    available_gpu = 0
    available_mem = 1000
    network_usage = 0

    if configure:
        server_id = input('server_id: ')
        region = input('region: ')
        name = input('name: ')



    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        # Hardcoded
        server_address = 'localhost', 8002
        connected = False
        while not connected:
            try:
                time.sleep(5)
                s.connect(server_address)
                connected = True
            except ConnectionRefusedError:
                print('Connecttion Refused. Retry after 5 secs.')
                connected = False


        # Network stats using 'ifstat'
        p_ifstat = subprocess.Popen(['ifstat', '-n'], stdout=subprocess.PIPE)
        if tegrastats_flag:
            p_tegrastats = subprocess.Popen('tegrastats', stdout=subprocess.PIPE)
        # Consume headers
        p_ifstat.stdout.readline()
        p_ifstat.stdout.readline()
        # Read contents
        while(True):
            time.sleep(1)
            ifstat = p_ifstat.stdout.readline().split()
            # server_state['network'] = dict(zip(['in', 'out'], list(map(float, ifstat))))
            network_usage = sum(list(map(float, ifstat)))
            if tegrastats_flag:
                tegrastats = p_tegrastats.stdout.readline().split()
                mem = tegrastats[1].decode().split('/')
                mem_used = int(mem[0])
                mem_total = int(mem[1].split('M')[0])
                available_mem = mem_total - mem_used
                cpus = tegrastats[9].decode().strip('[]').split(',')
                available_cpu = sum([int(cpu.split('%')[0]) for cpu in cpus])/len(cpus)
                available_gpu = int(tegrastats[13].decode().split('%')[0])
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
    parser.add_argument(
        '-t',
        '--tegrastats',
        action='store_true',
        help='Collect tegrastats info',
    )
    args = parser.parse_args()
    run(args.load, args.configure, args.tegrastats)


if __name__ == '__main__':
    main()
