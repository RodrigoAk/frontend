import selectors
import socket

HOST = '0.0.0.0'  # Symbolic name meaning all available interfaces
PORT = 50007  # Arbitrary non-privileged port

sel = selectors.DefaultSelector()


def accept(sock, mask):
    conn, addr = sock.accept()  # Should be ready
    print('Connected by', addr)
    conn.setblocking(False)
    sel.register(conn, selectors.EVENT_READ, read)


def read(conn, mask):
    data = b''
    while True:
        try:
            received = conn.recv(8)  # Should be ready
        except Exception as e:
            print(e)
            break
        if len(received) <= 0:
            break
        data += received
    print()
    print('Recebido: \n', data.decode('utf-8', 'ignore'))
    command = 'dir'
    if data:
        print('echoing', repr(command), 'to', conn)
        conn.send(command.encode())  # Hope it won't block
    else:
        print('closing', conn)
        sel.unregister(conn)
        conn.close()


sock = socket.socket()
sock.bind((HOST, PORT))
sock.listen(100)
sock.setblocking(False)
sel.register(sock, selectors.EVENT_READ, accept)

while True:
    events = sel.select()
    for key, mask in events:
        callback = key.data
        callback(key.fileobj, mask)
