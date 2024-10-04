from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from client.models import Client

@receiver(post_save, sender=User)
def create_or_save_client(sender, instance, created, **kwargs):
    if created:
        Client.objects.create(user=instance)
    instance.client.save()