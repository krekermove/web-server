# Generated by Django 4.2.6 on 2024-09-03 19:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('post', '0005_rename_content_ru_post_content_latin'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='slug',
            field=models.CharField(blank=True, default='', max_length=256, null=True),
        ),
    ]
