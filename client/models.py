import datetime

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.db import models
from rest_framework.exceptions import PermissionDenied, AuthenticationFailed

from user.models import SubscriptionType, Subscription
from user.subscription_serializer import SubscriptionSerializer

User = get_user_model()

# Create your models here.

class Client(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='client', verbose_name='Пользователь')
    paid = models.BooleanField(default=False, verbose_name='Оплачено')
    subscription_type = models.ForeignKey(SubscriptionType, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.user.username

    def get_active_subscription(self):
        try:
            return Subscription.objects.get(user=self.user, is_active=True)
        except:
            return None

    def end_date(self, subscription_type):
        date = datetime.datetime.today()
        if subscription_type.name == "VIP":
            year = 3000
            month = date.month
        else:
            month = date.month + int(subscription_type.period)
            year = date.year
            if month > 12:
                month %= 12
                year += 1
        end_date = datetime.datetime(year=year, month=month,
                                     day=date.day, hour=date.hour,
                                     minute=date.minute, second=date.second,
                                     microsecond=date.microsecond)
        return end_date

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        if not self._state.adding and self.subscription_type is not None:
            self.paid = True
            data = {}
            data['user'] = self.user.id
            data['subscription'] = self.subscription_type.id
            subscription = self.get_active_subscription()
            if subscription:
                data['end_date'] = subscription.end_date
                data['is_active'] = subscription.is_active
                serializer = SubscriptionSerializer(subscription, data=data)
                if serializer.is_valid():
                    serializer.save()
            else:
                data['end_date'] = self.end_date(self.subscription_type)
                serializer = SubscriptionSerializer(data=data)
                if serializer.is_valid():
                    serializer.save()
                    group_subscribers = Group.objects.get(name='Subscriber')
                    group_subscribers.user_set.add(self.user)
        return super().save(force_insert, force_update, using, update_fields)

    class Meta:
        verbose_name = 'Клиент'
        verbose_name_plural = 'Клиенты'


class ClientDevice(models.Model):
    device_id = models.CharField(max_length=128)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='devices')
    update_at = models.DateTimeField(auto_now=True)
    create_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        indexes = [
            models.Index(fields=['device_id'])
        ]
        unique_together = ('user', 'device_id')
        verbose_name = 'Устройство'
        verbose_name_plural = 'Устройства'
        
    @classmethod
    def get_or_create_device(cls, user, device_id):
        try:
            user_devices = cls.objects.get(user=user)
        except:
            user_devices = None
        if user_devices:
            if user_devices.device_id != device_id:
                raise PermissionDenied(detail='Кечирсиз, сизнинг аккаунтингизга бирдан зиёд телефон орқали кирилган, бу бизнинг иловамизни истифода қилиш келишувига мувофик.')

        device, created = cls.objects.get_or_create(user=user, device_id=device_id)
        device.is_active = True
        device.save()
        return device


    @classmethod
    def get_active_device(cls, user):
        try:
            return cls.objects.get(user=user, is_active=True)
        except cls.DoesNotExist:
            raise AuthenticationFailed(detail='Device with provided ID not found')
        except cls.MultipleObjectsReturned:
            cls.objects.filter(user=user).update(is_active=False)
            raise AuthenticationFailed(detail='Device with provided ID not found')

