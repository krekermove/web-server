# import asyncio
#
# from django.core.management.base import BaseCommand
# from aiogoogletrans import Translator
# from bs4 import BeautifulSoup
# from post.models import Post, Translations
# from asgiref.sync import sync_to_async
#
#
# class Command(BaseCommand):
#     help = 'Translate Uzbek CKEditor content to English asynchronously'
#
#     async def translate_text(self, text, translator):
#         if text and text.strip():
#             translation = await translator.translate(text, src='ru', dest='en')
#             return translation.text
#         return ' '
#
#     async def process_post(self, post, translator):
#         try:
#             soup_uz = BeautifulSoup(post.content, 'html.parser')
#             soup_en = BeautifulSoup(post.content_ru, 'html.parser')
#             original_text_uz = []
#             original_text_en = []
#             for element in soup_uz.find_all(text=True):
#                 original_text_uz.append(element.string)
#
#             for element in soup_en.find_all(text=True):
#                 original_text_en.append(element.string)
#
#             content_uz = '\n'.join(original_text_uz)
#             content_en = '\n'.join(original_text_en)
#             await Translations.objects.acreate()
#             tr = await sync_to_async(Translations.objects.get(content_uz__isnull=True))()
#             tr.content_uz = content_uz
#             tr.content_en = content_en
#             print(tr.content_uz)
#             print(tr.content_en)
#             # await sync_to_async(translations.save)()
#             self.stdout.write(self.style.SUCCESS(f'Successfully translated post {post.id}'))
#         except Exception as e:
#             self.stdout.write(self.style.ERROR(f'Error translating post {post.id}: {e}'))
#
#     async def handle_async(self):
#         translator = Translator()
#         posts = await sync_to_async(list)(Post.objects.all())
#
#         # tasks = [self.process_post(post, translator) for post in posts]
#         tasks = self.process_post(posts[0], translator)
#         await asyncio.gather(tasks)
#
#     def handle(self, *args, **kwargs):
#         asyncio.run(self.handle_async())

import re

from django.core.management.base import BaseCommand
from bs4 import BeautifulSoup
from post.models import Post, Translations

class Command(BaseCommand):
    help = 'Translate Uzbek CKEditor content to English'

    def handle(self, *args, **kwargs):
        posts = Post.objects.filter()

        for post in posts:
            try:
                soup_uz = BeautifulSoup(post.content, 'html.parser')
                soup_en = BeautifulSoup(post.content_latin, 'html.parser')
                original_text_uz = []
                original_text_en = []
                for element in soup_uz.find_all(text=True):
                    original_text_uz.append(element.string)

                for element in soup_en.find_all(text=True):
                    original_text_en.append(element.string)

                content_uz = ' '.join(original_text_uz)
                content_en = ' '.join(original_text_en)

                Translations.objects.create(content_uz=content_uz, content_en=content_en)
                self.stdout.write(self.style.SUCCESS(f'Successfully translated post {post.id}'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error translating post {post.id}: {e}'))

# class Command(BaseCommand):
#     help = 'Translate Uzbek CKEditor content to English'
#
#     def handle(self, *args, **kwargs):
#         posts = Translations.objects.filter()
#
#         for post in posts:
#             try:
#                 post.delete()
#                 self.stdout.write(self.style.SUCCESS(f'Successfully translated post {post.id}'))
#             except Exception as e:
#                 self.stdout.write(self.style.ERROR(f'Error translating post {post.id}: {e}'))
