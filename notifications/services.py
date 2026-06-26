from .models import Notification


def create_notification(
        *,
        receiver,
        sender,
        notification_type,
        startup=None
):

    return Notification.objects.create(
        receiver=receiver,
        sender=sender,
        startup=startup,
        notification_type=notification_type,
        is_read=False
    )