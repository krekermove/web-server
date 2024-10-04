from rest_framework import generics, renderers, viewsets, filters
from rest_framework.decorators import action
from rest_framework.mixins import ListModelMixin
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from . import custom_filter

from user.permissions import IsSubscriberUser, IsManagerUser
from .models import (
    Category,
    Post
)

from .serializers import (
    CategorySerializer,
    PostSerializer
)


class CategoryListView(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        startswith = self.request.query_params.get('startswith')
        if startswith:
            if startswith in "абвгдеёжзийклмнопрстуфхцчшщъыьэюяқғҳўАБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯҚҒҲЎ":
                queryset = queryset.filter(name__istartswith=startswith)
            elif startswith in "abvgdeyojziyklmnoprstufxtschshʼ'eyuyaqgʻhoʻABVGDEYOJZIYKLMNOPRSTUFXTSCHSHEYUYAQGʻHOʻ":
                queryset = queryset.filter(name_latin__istartswith=startswith)
        
        queryset = queryset.exclude(id=180)
        queryset = queryset.exclude(id=358)
        return queryset
    

class CategoryView(generics.RetrieveAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    filter_backends = [custom_filter.PostSearchFilter]
    search_fields = ['slug', 'slug_lat']
    renderer_classes = [renderers.JSONRenderer, renderers.TemplateHTMLRenderer]

    template_name = 'post.html'

    def get_queryset(self):
        queryset = super().get_queryset()
        category_id = self.request.query_params.get('category_id')
        if category_id:
            main_post2 = Category.objects.get(id=category_id).main_post2
            main_post3 = Category.objects.get(id=category_id).main_post3
            arr = list(queryset.filter(category_id=category_id))
            queryset = []
            if main_post3 or main_post2:
                for i in range(len(arr) - 1):
                    if arr[i].name == main_post2.name:
                        queryset.append(arr[i])
                        arr.pop(i)
                for i in range(len(arr) - 1):
                    if arr[i].name == main_post3.name:
                        queryset.append(arr[i])
                        arr.pop(i)
            arr.reverse()
            queryset += arr
        return queryset

    def get_permissions(self):
        if self.action == 'list':
            permission_classes = []
        elif self.action == 'retrieve':
            permission_classes = [IsSubscriberUser]
        else:
            permission_classes = [IsAdminUser]
        return [permission() for permission in permission_classes]

    # def update(self, request, *args, **kwargs):
    #     partial = kwargs.pop('partial', False)
    #     instance = self.get_object()
    #     if request.user.groups.filter(name='Manager').exists():
    #         instance.changed_by_manager = True
    #     serializer = self.get_serializer(instance, data=request.data, partial=partial)
    #     serializer.is_valid(raise_exception=True)
    #     self.perform_update(serializer)
    #
    #     if getattr(instance, '_prefetched_objects_cache', None):
    #         instance._prefetched_objects_cache = {}
    #
    #     return Response(serializer.data)

    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser],
            serializer_class=CategorySerializer)
    def set_main_post(self, request, pk):
        try:
            post = Post.objects.get(id=pk)
        except Post.DoesNotExist:
            return Response({'error': 'Пост не найден'}, status=400)
        category = CategorySerializer(request.data)
        if category.is_valid():
            category.main_post = post
            if request.data['file']:
                category.img = request.data['file']
            category.save()
            return Response(CategorySerializer(category).data)

