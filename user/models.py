from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()

# Create your models here.
class SubscriptionType(models.Model):
    name = models.CharField(max_length=50)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    period = models.PositiveIntegerField()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Тип подписки"
        verbose_name_plural = "Типы подписки"

class Subscription(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    subscription = models.ForeignKey(SubscriptionType, on_delete=models.CASCADE, null=True)
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user.username} - {self.subscription.name}"

    class Meta:
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"