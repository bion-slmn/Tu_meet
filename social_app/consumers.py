import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer

class NotificationConsumer(WebsocketConsumer):
    def connect(self):
        self.user = self.scope['user']
        if self.user.is_authenticated:
            self.user.channel_name = self.channel_name
            self.user.save()
            self.accept()
            print(f"User {self.user.username} connected.")
        else:
            self.close()

    def disconnect(self, close_code):
        self.user.channel_name = None

    def send_notification(self, event):
        self.send(text_data=json.dumps({ 'message': event['message'] }))