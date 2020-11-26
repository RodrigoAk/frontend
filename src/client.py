import asyncio
import websockets
import shlex


class Client:
    def __init__(self, server, websocket, path):
        self.client = websocket
        self.server = server
        self.name = None
        self.is_first_conn = True

    @property
    def connected(self):
        return self.client.open

    async def manage(self):
        try:
            while True:
                message = await self.receive()
                if message:
                    print(f"{self.name} < {message}")
                    await self.process_commands(message)
                else:
                    continue
        except Exception:
            print("Erro")
            raise
        finally:
            await self.disconnect()

    async def process_commands(self, message):
        if message.strip().startswith("/"):
            commands = shlex.split(message.strip()[1:])
            if len(commands) == 0:
                await self.send("Comando inválido")
                return
            print(commands)
            command = commands[0].lower()
            if command == 'nome':
                await self.change_name(commands, self.is_first_conn)
            elif command == 'pv':
                await self.send_private(commands)
            elif command == 'dc':
                await self.disconnect()
            else:
                await self.send('Comando desconhecido')
        else:
            if self.name:
                await self.server.send_to_all(self, message)
            else:
                await self.send("Identifique-se para enviara mensagens. Use o comando /nome SeuNome")

    async def change_name(self, commands, is_first_conn):
        if len(commands) > 1 and self.server.verify_name(commands[1]):
            if is_first_conn:
                self.is_first_conn = False
                self.name = commands[1]
                await self.send(f"Nome alterado com sucesso para {self.name}")
                await self.server.send_to_all(self, f'{self.name} aterrisou!')
            else:
                last_name = self.name
                self.name = commands[1]
                await self.send(f"Nome alterado com sucesso para {self.name}")
                await self.server.send_to_all(self, f'Nome alterado de {last_name} para {self.name}')
        else:
            await self.send("Nome em uso ou inválido. Escolha um outro.")

    async def send_private(self, commands):
        if len(commands) < 3:
            await self.send("Comando incorreto. /apenas Destinatário mensagem")
            return
        receiver = commands[1]
        message = " ".join(commands[2:])
        sent = await self.server.send_to_receiver(self, message, receiver)
        if not sent:
            await self.send(f"Destinatário {receiver} não encontrado. Mensagem não enviada.")

    async def send(self, message):
        await self.client.send(message)

    async def receive(self):
        message = await self.client.recv()
        return message

    async def disconnect(self):
        await self.server.disconnect(self)

