import subprocess
import socket

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    # load_balancer_address = '3.36.64.61', 59931
    load_balancer_address = 'localhost', 64001
    s.connect(load_balancer_address)

    server_state = {
        'server_name': 'my_jetson_nano',
        'serving_address': '222:111:222:238:8501',
        'available_models': 'should be scanned automatically'
        'various_hardware_status': 'staic performance like total available mem and dynamic performance like gpu usage'
    }
    
    # MODIFY the code to send the server_state instead of raw tegrastats
    
    p = subprocess.Popen('tegrastats', stdout=subprocess.PIPE)
    for line in iter(p.stdout.readline, b''):
        message = line
        sock.sendall(message)