import asyncio

from django.core.management.base import BaseCommand
# from aiogoogletrans import Translator
from bs4 import BeautifulSoup
from post.models import Post
from asgiref.sync import sync_to_async
from post.transliterator import UzbekLanguagePack


class Command(BaseCommand):
    help = 'Translate Uzbek CKEditor content to English asynchronously'

    # async def translate_text(self, text, translator):
    #     if text and text.strip():
    #         translation = await translator.translate(text, src='ru', dest='en')
    #         return translation.text
    #     return ' '

    async def transliterate_text(self, text):
        return UzbekLanguagePack().translit(text)

    async def process_post(self, post):
        try:
            soup = BeautifulSoup(post.content, 'html.parser')
            tasks = []
            for element in soup.find_all(text=True):
                original_text = element.string
                # if original_text and original_text.strip():
                tasks.append(self.transliterate_text(original_text))

            translations = await asyncio.gather(*tasks)

            for element, translation in zip(soup.find_all(text=True), translations):
                original_text = element.string
                if original_text:
                    element.replace_with(translation)

            post.content_latin = str(soup)
            print(post.content_latin)
            # await sync_to_async(post.save)()
            self.stdout.write(self.style.SUCCESS(f'Successfully translated post {post.id}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error translating post {post.id}: {e}'))

    async def handle_async(self):
        # translator = Translator()
        posts = await sync_to_async(list)(Post.objects.filter())

        # tasks = [self.process_post(post) for post in posts]
        tasks = self.process_post(posts[0])
        await asyncio.gather(tasks)

    def handle(self, *args, **kwargs):
        asyncio.run(self.handle_async())
