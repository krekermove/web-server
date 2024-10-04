import asyncio

from django.core.management.base import BaseCommand
# from aiogoogletrans import Translator
from bs4 import BeautifulSoup
from post.models import Post, Category
from asgiref.sync import sync_to_async
from post.transliterator import UzbekLanguagePack


class Command(BaseCommand):
    help = 'Translate Uzbek CKEditor content to English'

    def handle(self, *args, **kwargs):
        categories = Category.objects.all()
        posts = Post.objects.all()

        for post in posts:
            try:
                if "https://nadir-" in post.content:
                    print(post.id)
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error translating post {post.id}: {e}'))
