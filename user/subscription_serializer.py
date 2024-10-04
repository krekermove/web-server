from rest_framework import serializers

from user.models import SubscriptionType, Subscription
from user.validators import subscription_update


class SubscriptionTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscriptionType
        fields = '__all__'


class SubscriptionSerializer(serializers.ModelSerializer):

    def validate(self, subscription):
        subscription = subscription_update.validate(subscription)
        return subscription

    class Meta:
        model = Subscription
        fields = '__all__'