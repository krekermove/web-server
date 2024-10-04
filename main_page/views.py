from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from .models import SocialMedia, MainPage
from .serializers import MainPageSerializer


class MainPageAPIView(GenericAPIView):
    serializer_class = MainPageSerializer

    def get_social_media(self):
        try:
            return SocialMedia.objects.all()
        except:
            return None

    def get_main_page(self):
        try:
            return MainPage.objects.all()[0]
        except:
            return None

    def get(self, request):
        social_media = self.get_social_media()
        main_page = self.get_main_page()
        data = {
            'social_medias': social_media,
            'img': main_page.img,
            'first_btn': main_page.first_btn,
            'second_btn': main_page.second_btn,
            'third_btn': main_page.third_btn,
            'first_btn_lat': main_page.first_btn_lat,
            'second_btn_lat': main_page.second_btn_lat,
            'third_btn_lat': main_page.third_btn_lat,
            'link': main_page.link
        }
        serializer = MainPageSerializer(data)
        return Response(serializer.data)
