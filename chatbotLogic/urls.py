from django.urls import path
from .views import *
from rest_framework_simplejwt.views import (
    TokenRefreshView,
)

urlpatterns = [
    path('chat/', ChatbotAPI.as_view(), name='chatbot_api'),
    path('chat/rename', RenameChatAPI.as_view(), name='rename_chat'),
    path('chat/update', UpdateMessageAPI.as_view(), name='update_message'),
    path('auth/register', RegisterAPI.as_view(), name='register_api'),
    # path('auth/login', LoginAPI.as_view(), name='login_api'),
    path('auth/token', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/info', UserInfoAPI.as_view(), name='user_info_api'),
]