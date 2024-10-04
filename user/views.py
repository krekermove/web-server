import datetime

import pytz
from django.http import Http404
from rest_framework import status
from rest_framework.generics import CreateAPIView, GenericAPIView
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from django.contrib.auth import authenticate, login, get_user_model, logout
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.authentication import BasicAuthentication
from rest_framework.exceptions import AuthenticationFailed, ValidationError
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import Group

from client.models import ClientDevice
from medical_inventory import settings
from user.authentication import TokenAuthentication
from .models import SubscriptionType, Subscription
from .serializers import LogOutSerializer, UserSerializer, LoginSerializer
from .subscription_serializer import SubscriptionSerializer, SubscriptionTypeSerializer

User = get_user_model()


class SignUpView(CreateAPIView):
    authentication_classes = []
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def create(self, request, *args, **kwargs):
        if User.objects.filter(username=request.data['username']).exists():
            return Response({'details': 'Бундай номга ега фойдаланувчи аллақачон мавжуд.'}, status=400)
        elif len(request.data['password']) < 6:
            return Response({'details': 'Парол узунлиги 6 белгидан.'}, status=400)
        elif not request.data['username']:
            return Response({'details': 'Сиз фойдаланувчи номингизни киритишни унутдингиз.'}, status=400)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class TokenLogin(GenericAPIView):
    queryset = Token.objects.all()
    serializer_class = LoginSerializer
    authentication_classes = []
    
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data['username']
            password = serializer.validated_data['password']
            user = authenticate(request, username=username, password=password)
            device_id = request.data.get('device_id')
            if not user:
                return Response({'details': 'Бу фойдаланувчи номи билан ҳисоб йўқ.'}, status=400)
            login(request, user)
            ClientDevice.get_or_create_device(user=user, device_id=device_id)
            token, created = Token.objects.get_or_create(user=user)
            request.data['username'] = user
            if not created:
                return Response({"details": "Кечирсиз, сизнинг аккаунтингизга бирдан зиёд телефон орқали кирилган, бу бизнинг иловамизни истифода қилиш келишувига мувофик."}, status=400)
            return Response({**UserSerializer(user).data, 'token': token.key}, status=200)
        
        return Response(serializer.errors, status=400)


class TokenLogout(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        device = ClientDevice.get_active_device(request.user.id)
        device.is_active = False
        device.save()
        Token.objects.filter(user=request.user).delete()
        logout(request)
        return Response(status=204)


class TokenMe(GenericAPIView):
    serializer_class = UserSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(UserSerializer(request.user).data)


class SubscriptionTypeView(GenericAPIView):
    queryset = SubscriptionType
    serializer_class = SubscriptionTypeSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        pk = self.request.query_params.get('pk', None)
        try:
            queryset = SubscriptionType.objects.get(pk=pk)
        except:
            raise ValidationError("Invalid input")
        return queryset

    def get(self, request):
        subscriptions = SubscriptionType.objects.all()
        serializer = SubscriptionTypeSerializer(subscriptions, many=True)
        return Response(serializer.data)


class SubscriptionView(GenericAPIView):
    queryset = Subscription.objects.all()
    serializer_class = SubscriptionSerializer
    permission_classes = [IsAuthenticated]

    def get_subscription_type(self, pk):
        try:
            return SubscriptionType.objects.get(pk=pk)
        except:
            raise Http404

    def get_active_subscription(self, user):
        try:
            return Subscription.objects.get(user=user, is_active=True)
        except:
            return None

    def end_date(self, subscription_type):
        date = datetime.datetime.today()
        if subscription_type.name == "VIP":
            year = 3000
            month = date.month
        else:
            month = date.month + int(subscription_type.period)
            year = date.year
            if month > 12:
                month %= 12
                year += 1
        end_date = datetime.datetime(year=year, month=month,
                                     day=date.day, hour=date.hour,
                                     minute=date.minute, second=date.second,
                                     microsecond=date.microsecond)
        return end_date

    def get(self, request, pk):
        subscription_type = self.get_subscription_type(pk)
        request.data['user'] = request.user.id
        request.data['subscription'] = subscription_type.id
        subscription = self.get_active_subscription(request.user.id)
        if subscription:
            request.data['end_date'] = subscription.end_date
            request.data['is_active'] = subscription.is_active
            serializer = SubscriptionSerializer(subscription, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
        else:
            request.data['end_date'] = self.end_date(subscription_type)
            serializer = SubscriptionSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                group_subscribers = Group.objects.get(name='Subscriber')
                group_subscribers.user_set.add(request.user)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
