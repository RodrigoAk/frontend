import socket
import subprocess
import shlex


HOST = 'localhost'
PORT = 50007

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    s.sendall(b'hello')

    command = s.recv(1024)
    command = command.decode('utf-8')
    command = shlex.split(command)
    print('Comando a ser executado:', repr(command))
    p1 = subprocess.run(
        args=command,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT
    )
    s.sendall(p1.stdout)
