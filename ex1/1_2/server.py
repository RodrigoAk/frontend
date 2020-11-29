import selectors
import socket
import threading


HOST = '0.0.0.0'
PORT = 50007
command = b'dir'

sel = selectors.DefaultSelector()


def accept(sock, mask):
    conn, addr = sock.accept()  # Should bee ready
    print('Connected by:', addr)
    conn.setblocking(False)
    sel.register(conn, selectors.EVENT_READ, read)


def read(conn, mask):
    global command
    data = b''
    while True:
        try:
            received = conn.recv(1024)  # Should be ready
        except Exception:
            break
        if len(received) <= 0:
            break
        data += received
    if data:
        print('> Received:\n', repr(data))
        print()
        print('> Echoing', repr(command), 'to', conn)
        conn.send(command)  # Hope it won't block
    else:
        print('closing', conn)
        sel.unregister(conn)
        conn.close()


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
        callback(key.fileobj, mask)
