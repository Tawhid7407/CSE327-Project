from .models import Notification


def create_notification(user, message, link=''):
    """
    Create and store a dashboard notification for a user.

    :param user: The User instance who will receive the notification.
    :param message: Short text describing the notification event.
    :param link: Optional URL the notification should redirect to when clicked.
    :return: The created Notification instance.
    """
    return Notification.objects.create(user=user, message=message, link=link)
