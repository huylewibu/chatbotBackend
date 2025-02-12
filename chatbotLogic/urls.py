from django.urls import path
from .views import *
from rest_framework_simplejwt.views import (
    TokenRefreshView,
)

urlpatterns = [
    path('chat/', ChatbotAPI.as_view(), name='chatbot_api'),
    path('add-chat/', AddChatAPI.as_view(), name='add_chat_api'),
    path('get-chat/', GetChatsAPI.as_view(), name='get_chats_api'),
    path('get-messages/<chat_id>', GetMessagesByChatAPI.as_view(), name='get_messages_by_chat_api'),
    path('chat/rename', RenameChatAPI.as_view(), name='rename_chat'),
    path('chat/remove/<chat_id>', RemoveChatApi.as_view(), name='remove_chat'),
    path('chat/update', UpdateMessageAPI.as_view(), name='update_message'),
    path('auth/register', RegisterAPI.as_view(), name='register_api'),
    path('auth/token', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/info', UserInfoAPI.as_view(), name='user_info_api'),
    path('upload-files/', DocumentProcessingView.as_view(), name='upload_files'),
    path('generate-image/', GenerateImageAPI.as_view(), name='generate_image'),
]