from django.contrib import admin

from main_page.models import SocialMedia, MainPage


@admin.register(SocialMedia)
class SocialMediaAdmin(admin.ModelAdmin):
    list_display = ('id', 'icon', 'link')


@admin.register(MainPage)
class MainPageAdmin(admin.ModelAdmin):
    list_display = ('first_btn', 'second_btn', 'third_btn', 'img', 'link')
