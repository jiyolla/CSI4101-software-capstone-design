import subprocess
import socket
import json
import time

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    # load_balancer_address = '3.36.64.61', 59931
    load_balancer_address = 'localhost', 8002
    s.connect(load_balancer_address)

    # Collect server state info
    server_state = {
        'server_name': 'my_jetson_nano',
        'serving_address': '222:111:222:238:8501',
        'available_models': 'should be scanned automatically',
    }

    # Network stats using 'ifstat'
    p_ifstat = subprocess.Popen('ifstat', stdout=subprocess.PIPE)
    p_tegrastats = subprocess.Popen('tegrastats', stdout=subprocess.PIPE)
    # Consume headers
    p_ifstat.stdout.readline()
    p_ifstat.stdout.readline()
    # Read contents
    # for line in iter(p_ifstat.stdout.readline, b''):
    while(True):
        time.sleep(1)
        ifstat = p_ifstat.stdout.readline().split()
        server_state['network'] = dict(zip(['in', 'out'], list(map(float, ifstat))))
        tegrastats = p_tegrastats.stdout.readline().split()
        server_state['RAM'] = tegrastats[1].decode()
        server_state['CPU'] = tegrastats[9].decode()
        server_state['GPU'] = tegrastats[13].decode()
        data = json.dumps(server_state).encode('utf-8')
        s.sendall(len(data).to_bytes(4, 'big'))
        s.sendall(data)
