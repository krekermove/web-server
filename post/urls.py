from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register(r'', views.PostViewSet)

urlpatterns = [
    path('categories', views.CategoryListView.as_view(), name='category-list'),
    path('categories/<int:pk>', views.CategoryView.as_view(), name='category-detail'),
    path('', include(router.urls), name='posts'),
]
