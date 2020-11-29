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
        """Metodo para verificar se a conexao do cliente esta aberta ou nao.

        Returns:
            True: caso esteja aberta
            False: caso nao esteja aberta
        """
        return self.client.open

    async def manage(self):
        """Metodo principal do Client que gerencia as mensagens enviadas pelo
        usuario pelo client. Fica em em um loop infinito lendo as mensagens
        e processando. Caso o client seja fechado ele desconecta.
        """
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
        """Metodo para processar os comandos do chat inseridos pelo usuario.

        Args:
            message (str): Mensagem com os comandos inseridos.
        """
        if message.strip().startswith("/"):
            commands = shlex.split(message.strip()[1:])
            if len(commands) == 0:
                await self.send("Comando invalido")
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
        """Metodo para mudar o nome do usuario.

        Args:
            commands: lista com os parametros passado pelo usuario com o novo
                nome desejado
            is_first_conn: flag para verificar se e a primeira conexao do usuario
                para notificar a chegada dele para os outros usuarios.
        """
        if len(commands) > 1 and self.server.verify_name(commands[1]):
            if is_first_conn:
                self.is_first_conn = False
                self.name = commands[1]
                await self.send(f"Nome alterado com sucesso para {self.name}")
                await self.server.send_to_all(self, f'{self.name} entrou!')
            else:
                last_name = self.name
                self.name = commands[1]
                await self.send(f"Nome alterado com sucesso para {self.name}")
                await self.server.send_to_all(self, f'Nome alterado de {last_name} para {self.name}')
        else:
            await self.send("Nome em uso ou invalido. Escolha um outro.")

    async def send_private(self, commands):
        if len(commands) < 3:
            await self.send("Comando incorreto. /apenas Destinatario mensagem")
            return
        receiver = commands[1]
        message = " ".join(commands[2:])
        sent = await self.server.send_to_receiver(self, message, receiver)
        if not sent:
            await self.send(f"Destinatario {receiver} nao encontrado. Mensagem nao enviada.")

    async def send(self, message):
        """Metodo para enviar mensagens para o servidor.

        Args:
            message (str): mensagem a ser enviada
        """
        await self.client.send(message)

    async def receive(self):
        """Metodo para ler mensagens do client inseridas pelo usuario.

        Returns:
            message (str): mensagem inserida pelo usuario
        """
        message = await self.client.recv()
        return message

    async def disconnect(self):
        """Metodo para fechar a conexao do websocket."""
        await self.server.disconnect(self)

