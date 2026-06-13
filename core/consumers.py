import json

from channels.generic.websocket import AsyncWebsocketConsumer


class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        user = self.scope.get("user")
        if not user or user.is_anonymous:
            print(f"[WS REJECT] anonymous path={self.scope.get('path')}", flush=True)
            await self.close()
            return
        self.group_name = f"user_{user.id}"
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()
        print(f"[WS CONNECT] user={user.username} group={self.group_name}", flush=True)

    async def disconnect(self, close_code):
        if hasattr(self, "group_name"):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def notification_message(self, event):
        print(f"[WS SEND] user={getattr(self.scope.get('user'), 'username', 'unknown')} payload={event['payload'].get('title')}", flush=True)
        await self.send(text_data=json.dumps(event["payload"]))