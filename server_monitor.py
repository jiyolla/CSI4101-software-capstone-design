import subprocess
import socket

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
    my_goorm_addr = ('3.36.64.61', 59931)
    # ip, port = 'localhost', 64001
    # sock.connect((ip, port))
    sock.connect(my_goorm_addr)

    p = subprocess.Popen('tegrastats', stdout=subprocess.PIPE)
    for line in iter(p.stdout.readline, b''):
        message = line
        sock.sendall(message)