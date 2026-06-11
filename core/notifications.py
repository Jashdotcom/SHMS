from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from .models import Notification


def create_notification(*, recipient, title, message, notification_type=Notification.TYPE_INFO, related_url=""):
    notification = Notification.objects.create(
        recipient=recipient,
        title=title,
        message=message,
        notification_type=notification_type,
        related_url=related_url,
    )
    channel_layer = get_channel_layer()
    if channel_layer:
        async_to_sync(channel_layer.group_send)(
            f"user_{recipient.id}",
            {
                "type": "notification.message",
                "payload": {
                    "id": notification.id,
                    "title": notification.title,
                    "message": notification.message,
                    "notification_type": notification.notification_type,
                    "related_url": notification.related_url,
                    "created_at": notification.created_at.isoformat(),
                },
            },
        )
    return notification