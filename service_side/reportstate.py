import subprocess
import socket
import time
import argparse
import pickle
import json
import sys
import os

sys.path.append(os.path.join(sys.path[0], '..'))
from common import serverstate
from common import available_models


def run(tegrastats_flag):

    try:
        with open('report.config', 'rb') as f:
            config = json.load(f)
            server_address = config['monitor server ip'], config['monitor server port']
            region = config['region']
            name = config['name']
            ip = config['ip']
            port = config['port']
            
    except OSError as e:
        print('Failed to load config file')
        raise e

    # Collect server state info
    models = available_models.lst
    available_cpu = 0
    available_gpu = 0
    available_mem = 0
    network_usage = 0
    server_state = serverstate.ServerState(region, name, ip, port, models, available_cpu, available_gpu, available_mem, network_usage)
    
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
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
        print('Start sending server state...')
        
        # interval should be larger than drl observation interval for sync issue
        interval = 1
        while(True):
            time.sleep(interval)
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
            server_state.available_cpu = available_cpu
            server_state.available_gpu = available_gpu
            server_state.available_mem = available_mem
            server_state.network_usage = network_usage
            data = pickle.dumps(server_state)

            # Custom protocle: [4 bytes for data size] + [data]
            s.sendall(len(data).to_bytes(4, 'big'))
            s.sendall(data)


def main():
    parser = argparse.ArgumentParser(description='Collect and report system information')
    parser.add_argument(
        '-t',
        '--tegrastats',
        action='store_true',
        help='Collect tegrastats info',
    )
    args = parser.parse_args()
    run(args.tegrastats)


if __name__ == '__main__':
    main()
