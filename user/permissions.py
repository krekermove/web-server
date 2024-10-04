from django.http import Http404
from rest_framework import permissions
from post.models import Post


class IsManagerUser(permissions.BasePermission):

    def has_permission(self, request, view):
        if request.method == 'PUT' or request.method == 'PATCH':
            return True if request.user and request.user.groups.filter(name='Manager').exists() else False
        return False


class IsSubscriberUser(permissions.BasePermission):

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            try:
                post = Post.objects.get(id=int(request.parser_context['kwargs']['pk']))
            except Post.DoesNotExist:
                return Http404
            if not post.category.name[0] == 'А':
                if post.category.main_post:
                    if not post.category.main_post.id == post.id:
                        return request.user and request.user.groups.filter(name='Subscriber').exists()
                else:
                    print(int(post.position_in_category))
                    if not int(post.position_in_category) == int(Post.objects.filter(category_id=post.category).last().position_in_category):
                        return request.user and request.user.groups.filter(name='Subscriber').exists()
            return True
        return False
