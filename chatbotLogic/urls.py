from django.urls import path
from .views import ChatbotAPI, RenameChatAPI

urlpatterns = [
    path('chat/', ChatbotAPI.as_view(), name='chatbot_api'),
    path('chat/rename/', RenameChatAPI.as_view(), name='rename_chat'),
]