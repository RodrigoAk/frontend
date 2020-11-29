import socket
import subprocess
import shlex


HOST = 'localhost'
PORT = 50007

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    s.sendall(b'hello, server')
    first_conn = True
    ID = ''
    while True:
        command = s.recv(1024)
        command = command.decode('utf-8')
        if first_conn:
            ID = command
            print('My ID:', ID)
            first_conn = False
            s.sendall(f'{ID} wait'.encode())
        else:
            command = shlex.split(command)
            if ID == command[0]:
                command.pop(0)
                if command == ['quit']:
                    print('Closing connection...')
                    break
                elif command != ['wait']:
                    print('Comando a ser executado:', repr(command))
                    p1 = subprocess.run(
                        args=command,
                        shell=True,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT
                    )
                    message = f'{ID} '.encode() + p1.stdout
                    print()
                    s.sendall(message)
                else:
                    s.sendall(f'{ID} wait'.encode())
            else:
                s.sendall(f'{ID} wait'.encode())
