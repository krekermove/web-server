from django.urls import path
from . import views


urlpatterns = [
    path('', views.NotificationAPIView.as_view(), name='notifications'),
]