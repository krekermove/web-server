from django.db.models import QuerySet
from django.http import Http404
from rest_framework.generics import ListAPIView
from rest_framework.response import Response

from .models import Notification
from .serializers import NotificationSerializer


class NotificationAPIView(ListAPIView):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer

    def get_queryset(self):
        try:
            if self.request.user.groups.filter(name='Manager'):
                return Notification.objects.all()
            elif self.request.user.groups.filter(name='Subscriber'):
                return Notification.objects.filter(recipient_group__in=['Subscriber', 'Member'])
            return Notification.objects.filter(recipient_group='Member')
        except Notification.DoesNotExist:
            return Http404
