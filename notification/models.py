from django.contrib.auth.models import Group
from django.db import models
from rest_framework.exceptions import APIException
from post.models import Post


def get_user_groups():
    choices = []
    try:
        groups = Group.objects.all()
        for group in groups:
            t = ()
            t += (str(group.name), str(group.name))
            choices.append(t)
    except:
        raise APIException("Groups not found")
    return tuple(choices)


class Notification(models.Model):
    recipient_group = models.CharField(max_length=100, choices=get_user_groups(),
                                       null=True, blank=True, verbose_name="Группа получателей")
    message = models.TextField()
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Уведомление'
        verbose_name_plural = 'Уведомления'
        ordering = ["-created_at"]
