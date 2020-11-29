import socket
import subprocess
import shlex


HOST = 'localhost'  # The remote host
PORT = 50007

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    s.sendall(b'Hello, world')

    command = s.recv(1024)
    command = command.decode('utf-8')
    print('Comando a ser executado:', repr(command))
    command = shlex.split(command)
    p1 = subprocess.run(
        args=command,
        shell=True,
        stdout=subprocess.PIPE,   # Concatenate stdout and
        stderr=subprocess.STDOUT  # stderr in one PIPE
    )
    s.sendall(p1.stdout)
