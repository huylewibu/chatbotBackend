from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .logic.chatbot import generate_response, generate_chat_name

class ChatbotAPI(APIView):
    def post(self, request):
        user_input = request.data.get('message', '')
        chat_history = request.data.get('chat_history', [])
        if not user_input:
            return Response({"error": "No input provided"}, status=status.HTTP_400_BAD_REQUEST)

        # Xử lý logic chatbot
        try:
            bot_response = generate_response(user_input, chat_history)
            if not bot_response:
                bot_response = "Không nhận được phản hồi từ bot."  # Đáp ứng mặc định nếu không có kết quả
        except Exception as e:
            print(f"Error in generate_response: {e}")
            bot_response = "Lỗi xảy ra khi xử lý phản hồi từ bot."

        return Response({"user_message": user_input, "bot_response": bot_response})
    
class RenameChatAPI(APIView):
    def post(self, request):
        user_input = request.data.get('message', '')
        if not user_input:
            return Response({"error": "No input provided"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Gọi hàm generate_chat_name
            chat_name = generate_chat_name(user_input)
        except Exception as e:
            print(f"Error in generate_chat_name: {e}")
            chat_name = "Cuộc trò chuyện mới"

        return Response({"chat_name": chat_name})