from rest_framework.response import Response
from notification.serializers import NotificationSerializer


def notification_response(func):
    def wrapper(*args, **kwargs):
        func(*args, **kwargs)
        notification = type(args[0]).objects.all()[0]
        serializer = NotificationSerializer(notification)
        return Response(serializer.data)
    return wrapper