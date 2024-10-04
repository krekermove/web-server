from django.urls import path
from .views import *

urlpatterns = [
    path('sign_up', SignUpView.as_view()),
    path('token/login', TokenLogin.as_view()),
    path('token/logout', TokenLogout.as_view()),
    path('token/me', TokenMe.as_view()),
    # path('subscriptions', SubscriptionTypeView.as_view()),
    # path('subscriptions/<int:pk>', SubscriptionView.as_view()),
]
