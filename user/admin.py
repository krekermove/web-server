from django.contrib import admin
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User, Group
from rest_framework.authtoken.models import TokenProxy

from client.models import Client
from user.models import SubscriptionType, Subscription


class TokenAdmin(admin.ModelAdmin):
    search_fields = ['key', 'user__username']  # Add the key and related user's username to search_fields
    list_display = ['key', 'user']  # Customize the displayed fields

    def get_user(self, obj):
        return obj.user.username

    get_user.short_description = 'Username'

admin.site.register(Token, TokenAdmin)
admin.site.unregister(TokenProxy)

@admin.register(SubscriptionType)
class SubscriptionTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'period']

@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ['user', 'subscription', 'start_date', 'end_date', 'is_active']

    actions = ['delete_selected',]

    def get_actions(self, request):
        actions = super(SubscriptionAdmin, self).get_actions(request)
        return actions

    def delete_model(self, request, obj):
        group_subscribers = Group.objects.get(name='Subscriber')
        group_subscribers.user_set.remove(obj.user)
        client = Client.objects.get(user=obj.user)
        client.subscription_type = None
        client.paid = False
        client.save()
        obj.delete()

    def delete_selected(self, request, queryset):
        group_subscribers = Group.objects.get(name='Subscriber')
        for obj in queryset:
            group_subscribers.user_set.remove(obj.user)
            client = Client.objects.get(user=obj.user)
            client.subscription_type = None
            client.paid = False
            client.save()
        queryset.delete()

    delete_selected.short_description = 'Удалить выбранные подписки'
