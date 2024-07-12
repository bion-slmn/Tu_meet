from .models import Profile
from .models import (
    User, Comment, Like, Notification)
from django.db.models.signals import post_save
from django.dispatch import receiver
from typing import Union, List
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .serialiser import NotificationSerialiser


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    """
    Creates a profile for a newly created User instance.

    Returns:
        None
    """

    if created:
        profile = Profile.objects.create(user=instance)

def send_notification(
    notifications: List[Notification],
    channel_name: str,
    many: bool = False
) -> None:
    """
    Sends notifications to a specified channel using the 
    provided list of notifications.

    Args:
        notifications: A list of Notification instances to be sent.
        channel_name: The name of the channel to send the notifications to.
        many: A boolean indicating if multiple notifications are being sent.
    Returns:
        None
    """

    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.send)(
            channel_name,
            {
                "type": "send_notification",
                "message": NotificationSerialiser(notifications, many=many).data
            }
        )


def create_notification(instance: Union[Comment, Like], message: str) -> None:
    """
    Creates a notification based on the provided instance and message.

    Args:
        instance: The instance (Comment or Like) for which the notification is created.
        message: The message content for the notification.

    Returns:
        None
    """
    whose_post = instance.post.user.id
    who_created = instance.user

    if who_created.id != whose_post:
        message = f"{who_created.username} {message}"
        return Notification.objects.create(
                user=who_created,
                created_for=whose_post,
                message=message)
    
    
@receiver(post_save, sender=Comment)
def created_comment(sender, instance, created, **kwargs):
    """
    Handles the signal when a Comment instance is created.

    Args:
        sender: The sender of the signal.
        instance: The Comment instance that triggered the signal.
        created: A boolean indicating if the instance was created.
        **kwargs: Additional keyword arguments.

    Returns:
        None
    """

    if created:
        notifications = create_notification(instance, 'commented on your post')
        channel_name = User.objects.filter(id=notifications.created_for).channel_name
        if channel_name:
            send_notification(notifications, channel_name)

        

@receiver(post_save, sender=Like)
def created_comment(sender, instance, created, **kwargs):
    """
    Handles the signal when a Like instance is created.

    Args:
        sender: The sender of the signal.
        instance: The Like instance that triggered the signal.
        created: A boolean indicating if the instance was created.
        **kwargs: Additional keyword arguments.

    Returns:
        None
    """
    if created:
        notifications = create_notification(instance, 'liked your post')
        channel_name = User.objects.filter(id=notifications.created_for).channel_name
        if channel_name:
            send_notification(notifications, channel_name)



@receiver(post_save, sender=User)
def send_unread_notification(sender, instance, created, **kwargs):
    if created and instance.channel_name:
        notifications = Notification.objects.filter(
            created_for=instance.id, read=False)
        send_notification(notifications, instance.channel_name, many=True)