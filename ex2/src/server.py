import asyncio
import websockets
import shlex
from client import Client


class Server:
    def __init__(self):
        self.connections = []
        self.name = 'SERVER'

    @property
    def n_connections(self):
        """Metodo que retorna o numero de conexoes ativas."""
        return len(self.connections)

    async def connect(self, websocket, path):
        """Metodo para realizar a conexao do client com o servidor.

        Args:
            websocket: WebSockets object
        """
        client = Client(self, websocket, path)
        if client not in self.connections:
            self.connections.append(client)
            print(f"Novo cliente conectado. Total: {self.n_connections}")
        await client.manage()

    async def disconnect(self, client):
        """Metodo que remove o client a ser desconectado da lista de clients
        conectados, e efetivamente realiza a desconexao, avisando aos outros
        clients do ocorrido.

        Args:
            client (Client obj): client a ser desconectado
        """
        if client in self.connections:
            self.connections.remove(client)
            await self.send_to_all(self, f'{client.name} desconectou...')
            print(f"Cliente {client.name} desconectado. Total: {self.n_connections}")
            await client.client.close()

    def verify_name(self, name):
        """Metodo que verifica se o nome passado ja esta em uso.

        Args:
            name (str): Nome a ser verificado

        Returns:
            True: caso o nome esteja disponivel
            False: caso o nome nao esteja disponivel
        """
        for client in self.connections:
            if client.name and client.name == name:
                return False
        return True

    async def send_to_receiver(self, origin, message, receiver):
        """Metodo para enviar uma mensagem privada.

        Args:
            origin (Client obj): Client que esta enviando a mensagem
            message (str): mensagem a ser enviada
            receiver (Client obj): Client que ira receber a mensagem
        """
        for client in self.connections:
            if client.name == receiver and origin != client and client.connected:
                print(f"Enviando de <{origin.name}> para <{client.name}>: {message}")
                await client.send(f"PRIVADO de {origin.name} >> {message}")
                return True
        return False

    async def send_to_all(self, origin, message):
        """Metodo para enviar a mensagem de um client para todos os outros
        clients, exceto ele mesmo.

        Args:
            origin (Client obj): client que esta enviando a mensagem
            message (str): mensagem a ser enviada
        """
        print("Enviando a todos")
        for client in self.connections:
            if origin != client and client.connected:
                print(f"Enviando de <{origin.name}> para <{client.name}>: {message}")
                await client.send(f"{origin.name} >> {message}")


server = Server()
loop = asyncio.get_event_loop()

start_server = websockets.serve(server.connect, "localhost", 8765)

try:
    loop.run_until_complete(start_server)
    loop.run_forever()
finally:
    start_server.close()
