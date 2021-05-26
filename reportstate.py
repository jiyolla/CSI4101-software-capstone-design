import subprocess
import socket
import json

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    # load_balancer_address = '3.36.64.61', 59931
    load_balancer_address = 'localhost', 8002
    s.connect(load_balancer_address)

    # Collect server state info
    server_state = {
        'server_name': 'my_jetson_nano',
        'serving_address': '222:111:222:238:8501',
        'available_models': 'should be scanned automatically',
        'various_hardware_status': 'staic performance like total available mem and dynamic performance like gpu usage'
    }

    # Network stats using 'ifstat'
    p = subprocess.Popen('ifstat', stdout=subprocess.PIPE)
    # Consume headers
    p.stdout.readline()
    p.stdout.readline()
    # Read contents
    for line in iter(p.stdout.readline, b''):
        server_state['network'] = dict(zip(['in', 'out'], list(map(float, line.split()))))
        data = json.dumps(server_state).encode('utf-8')
        s.sendall(len(data).to_bytes(4, 'big'))
        s.sendall(data)
