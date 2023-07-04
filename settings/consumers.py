from channels.generic.websocket import AsyncWebsocketConsumer


class ActivationAccountConsumer(AsyncWebsocketConsumer):
    """Consumer for activate account."""

    async def connect(self):
        # Присоединение к группе 'account_activation'
        await self.channel_layer.group_add(
            'account_activation',
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        # Отсоединение от группы 'account_activation'
        await self.channel_layer.group_discard(
            'account_activation',
            self.channel_name
        )

    async def receive(self, text_data):
        # При получении сообщения, выполняется перенаправление на страницу авторизации
        await self.send_json(
            {'redirect': 'https://your-react-app.com/login'}
        )

