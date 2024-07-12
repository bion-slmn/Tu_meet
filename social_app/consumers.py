import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer

class NotificationConsumer(WebsocketConsumer):
    """
    WebSocket consumer for handling notifications.

    connect():
        Connects the user to the WebSocket and saves the user's channel name.

    disconnect(close_code):
        Disconnects the user from the WebSocket.

    send_notification(event):
        Sends a notification message over the WebSocket.
    """

    def connect(self):
        """
        Connects the user to the WebSocket if authenticated, 
        saves the user's channel name, and accepts the connection.

        Returns:
            None
        """

        self.user = self.scope['user']
        if self.user.is_authenticated:
            self.user.channel_name = self.channel_name
            self.user.save()
            self.accept()
            print(f"User {self.user.username} connected.")
        else:
            self.close()

    def disconnect(self, close_code):
        """
        Disconnects the user from the WebSocket by 
        setting the user's channel name to None.

        Args:
            close_code: The close code for the disconnection.

        Returns:
            None
        """

        self.user.channel_name = None

    def send_notification(self, event):
        """
        Sends a notification message over the WebSocket.

        Args:
            event: The event containing the notification message.

        Returns:
            None
        """
        self.send(text_data=json.dumps({ 'message': event['message'] }))