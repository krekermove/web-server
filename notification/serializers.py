from rest_framework import serializers


class NotificationSerializer(serializers.Serializer):
    recipient_group = serializers.CharField()
    message = serializers.CharField()
    post = serializers.IntegerField(source='post.id')
    created_at = serializers.DateTimeField()