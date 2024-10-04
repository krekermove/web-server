from django.core.management.base import BaseCommand
from post.models import Post, Category

class Command(BaseCommand):
    help = 'Update positions of posts within each category'

    def handle(self, *args, **kwargs):
        categories = Category.objects.all()
        for category in categories:
            posts = Post.objects.filter(category=category).order_by('id')
            for index, post in enumerate(posts, start=1):
                post.position_in_category = index
                post.save()
        self.stdout.write(self.style.SUCCESS('Successfully updated post positions'))