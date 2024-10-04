from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from rest_framework import serializers

from client.models import Client
from user.models import SubscriptionType, Subscription
from user.validators import subscription_update

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    paid = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'paid')
        extra_kwargs = {
            'password': {'write_only': True},
            'paid': {'read_only': True}
            }
        
    def create(self, validated_data):
        passwd = validated_data.pop("password") 
        user = User(**validated_data)
        user.set_password(passwd)
        user.save()
        group_subscribers = Group.objects.get(name='Member')
        group_subscribers.user_set.add(user)
        return user

    def get_paid(self, obj):
        try:
            client = Client.objects.get(user=obj)
            return client.paid
        except Client.DoesNotExist:
            return False

    def validate_email(self, value):
        email = value.lower()
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError("This email is already in use.")
        return email
    

class LogOutSerializer(serializers.Serializer):
    device_id = serializers.CharField(write_only=True)
   

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)
    device_id = serializers.CharField()
