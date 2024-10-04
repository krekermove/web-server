from django.db import models


class SocialMedia(models.Model):
    icon = models.ImageField(default=None, upload_to='./main_page/social_media/',
                            verbose_name='Иконка соцсети', null=True, blank=True)
    link = models.CharField(max_length=1000, verbose_name="Ссылка на соцсеть")

    class Meta:
        verbose_name = 'Социальная сеть'
        verbose_name_plural = 'Социальные сети'


class MainPage(models.Model):
    img = models.ImageField(default=None, upload_to='./main_page/social_media/',
                            verbose_name='Картинка на главной странице', null=True, blank=True)
    link = models.CharField(max_length=1000, null=True, blank=True, verbose_name="Ссылка")
    first_btn = models.CharField(max_length=100, verbose_name="Текст на первой кнопке")
    second_btn = models.CharField(max_length=100, verbose_name="Текст на второй кнопке")
    third_btn = models.CharField(max_length=100, verbose_name="Текст на третьей кнопке")
    first_btn_lat = models.CharField(max_length=100, default="", verbose_name="Текст на первой кнопке на латинице")
    second_btn_lat = models.CharField(max_length=100, default="", verbose_name="Текст на второй кнопке на латинице")
    third_btn_lat = models.CharField(max_length=100, default="", verbose_name="Текст на третьей кнопке на латинице")

    class Meta:
        verbose_name = 'Главная страница'
        verbose_name_plural = 'Главная страница'