import selectors
import socket
import threading

WAIT = 'wait'.encode()

HOST = '0.0.0.0'
PORT = 50007
command = WAIT
ID = 0

sel = selectors.DefaultSelector()


def accept(sock, mask):
    global command, ID, con
    conn, addr = sock.accept()  # Should bee ready
    print('Connected by:', addr)
    print('ID:', ID)
    conn.setblocking(False)
    con = Connection(conn, addr, ID)
    sel.register(conn, selectors.EVENT_READ, read)
    command = str(ID).encode()
    ID += 1


def read(conn, mask):
    global command, con
    data = b''
    while True:
        try:
            received = conn.recv(1024)  # Should be ready
        except Exception:
            break
        if len(received) <= 0:
            break
        data += received
    data = data.decode('utf-8', 'ignore')
    if data == 'hello, server':
        conn.send(command)
        command = command + b' wait'
    else:
        try:
            myID = data.split()[0]
            if myID == command.decode('utf-8').split()[0]:
                wait = myID.encode() + b' ' + WAIT
                if data.encode() != wait:
                    print('> Received:\n', data, '\n from:', conn)
                    print()
                if command != wait:
                    print('> Echoing', repr(command), 'to', conn)
                    conn.send(command)  # Hope it won't block
                    command = wait
                else:
                    conn.send(command)
            else:
                conn.send(command)
        except Exception:
            print('Closed connection...')
            print(con.print_all())
            sel.unregister(conn)
            conn.close()


class Connection:
    def __init__(self, conn, addr, ID):
        self.conn = conn
        self.ID = ID
        self.addr = addr

    def print_all(self):
        print('Conn:', self.conn, '\nAddr:', self.addr, '\nID:', self.ID)


def handle_input():
    global command
    while True:
        new_command = str(input()).encode()
        if new_command:
            command = new_command


sock = socket.socket()
sock.bind((HOST, PORT))
sock.listen(100)
sock.setblocking(False)
sel.register(sock, selectors.EVENT_READ, accept)
thread = threading.Thread(target=handle_input, daemon=True)
thread.start()

while True:
    events = sel.select()
    for key, mask in events:
        callback = key.data
        t = threading.Thread(target=callback, args=(key.fileobj, mask))
        t.run()
