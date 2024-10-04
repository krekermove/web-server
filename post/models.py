from bs4 import BeautifulSoup
from django.db import models
from django.urls import reverse
from django_ckeditor_5.fields import CKEditor5Field

from post.transliterator import UzbekLanguagePack


class Category(models.Model):
    name = models.CharField(max_length=256, verbose_name='Название')
    name_latin = models.CharField(max_length=256, verbose_name='Название на латыни', null=True, blank=True)
    slug = models.CharField(max_length=256, default="", null=True, blank=True)
    main_post = models.OneToOneField('Post', related_name='main_in_category',
                                     on_delete=models.SET_NULL, verbose_name='Главный пост 1', null=True, blank=True)
    main_post2 = models.OneToOneField('Post', related_name='main_in_category2',
                                     on_delete=models.SET_NULL, verbose_name='Главный пост 2', null=True, blank=True)
    main_post3 = models.OneToOneField('Post', related_name='main_in_category3',
                                     on_delete=models.SET_NULL, verbose_name='Главный пост 3', null=True, blank=True)
    img = models.ImageField(default=None, upload_to='./main_post/',
                            verbose_name='Обложка главного поста', null=True, blank=True)

    def __str__(self):
        return self.name

    def generate_slug(self):
        return self.name.lower()

    def transliterate_text(self, text):
        try:
            return UzbekLanguagePack().translit(text)
        except Exception as e:
            return e

    def save(self, *args, **kwargs):
        self.slug = self.generate_slug()
        self.name_latin = self.transliterate_text(self.name)
        super().save(*args, **kwargs)
        
    def get_absolute_url(self):
        return reverse('category-detail', kwargs={'pk': self.pk})

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        

class Post(models.Model):
    name = models.CharField(max_length=256, verbose_name='Название')
    name_latin = models.CharField(max_length=256, verbose_name='Название на латыни', null=True, blank=True)
    slug = models.CharField(max_length=256, default="", null=True, blank=True, editable=False)
    slug_lat = models.CharField(max_length=256, default="", null=True, blank=True, editable=False)
    create_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    update_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')
    published = models.BooleanField(verbose_name='Опубликован')
    content = CKEditor5Field(config_name='extends', verbose_name='Контент', null=True, blank=True)
    content_latin = CKEditor5Field(config_name='extends', verbose_name='Контент на латыни', null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='posts', verbose_name='Категория')
    changed_by_manager = models.BooleanField(default=False)
    position_in_category = models.PositiveIntegerField(default=0, editable=False, verbose_name='Позиция в категории')

    def get_absolute_url(self):
        return reverse('post-detail', kwargs={'pk': self.pk})
    
    def __str__(self) -> str:
        return self.name

    def generate_slug(self):
        return self.name.lower()

    def transliterate_slug(self, text):
        try:
            return UzbekLanguagePack().translit(text)
        except Exception as e:
            return e

    def transliterate_text(self, content):
        try:
            soup = BeautifulSoup(content, 'html.parser')
            tasks = []
            if len(self.content_latin) <= 89:
                for element in soup.find_all(text=True):
                    original_text = element.string
                    tasks.append(UzbekLanguagePack().translit(original_text))
            else:
                for element in soup.find_all(text=True):
                    original_text = element.string
                    tasks.append(UzbekLanguagePack().translit(original_text, reversed=True))

            for element, translation in zip(soup.find_all(text=True), tasks):
                original_text = element.string
                if original_text:
                    element.replace_with(translation)

            if len(self.content_latin) <= 89:
                self.content_latin = str(soup)
            elif len(self.content) <= 89:
                self.content = str(soup)

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error translating post: {e}'))

    def save(self, *args, **kwargs):
        if self._state.adding:
            max_position = Post.objects.filter(category=self.category).aggregate(
                models.Max('position_in_category'))['position_in_category__max']
            self.position_in_category = 1 if max_position is None else max_position + 1
            if len(self.content) > 89 >= len(self.content_latin):
                self.transliterate_text(self.content)
            elif len(self.content_latin) > 89 >= len(self.content):
                self.transliterate_text(self.content_latin)
            if not self.name_latin:
                self.name_latin = UzbekLanguagePack().translit(self.name)
        self.slug = self.generate_slug()
        self.slug_lat = self.transliterate_slug(self.slug)

        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        posts = list(Post.objects.filter(category=self.category))
        posts.pop(self.position_in_category - 1)
        for index, post in enumerate(posts, start=1):
            post.position_in_category = index
            post.save()
        super().delete(*args, **kwargs)

    class Meta:
        verbose_name = 'Пост'
        verbose_name_plural = 'Посты'


class Translations(models.Model):
    content_uz = CKEditor5Field(config_name='extends', verbose_name='Контент на узбекском')
    content_en = CKEditor5Field(config_name='extends', verbose_name='Контент на английском')

    class Meta:
        verbose_name = 'Перевод'
        verbose_name_plural = 'Переводы'