from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .logic.chatbot import generate_response, generate_chat_name
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class ChatbotAPI(APIView):
    def post(self, request):
        print("request 1: ", request.data)
        user_input = request.data.get('message', '')
        chat_history = request.data.get('chat_history', [])
        print("request: ", request.data)
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
    
class UpdateMessageAPI(APIView):
    def post(self, request):
        # Lấy dữ liệu từ request
        chat_id = request.data.get("chat_id", "")
        message_id = request.data.get("message_id", "")
        new_question = request.data.get("new_text", "")
        chat_history = request.data.get("chat_history", [])

        if not new_question:
            return Response({"error": "No input provided"}, status=status.HTTP_400_BAD_REQUEST)

        # Xử lý logic chatbot
        try:
            # Gửi câu hỏi đã chỉnh sửa đến bot
            bot_response = generate_response(new_question, chat_history)
            if not bot_response:
                bot_response = "Không nhận được phản hồi từ bot."  # Đáp ứng mặc định nếu không có kết quả
        except Exception as e:
            print(f"Error in generate_response: {e}")
            bot_response = "Lỗi xảy ra khi xử lý phản hồi từ bot."

        # Trả về phản hồi mới từ bot
        return Response({
            "message_id": message_id,
            "new_text": new_question,
            "bot_response": bot_response
        })
    
class RegisterAPI(APIView):
    def post(self, request):
        username = request.data.get("username")
        email = request.data.get("email")
        password = request.data.get("password")
        
        if not username or not email or not password:
            return Response({"error": "All fields are required."}, status=400)
        
        if User.objects.filter(username=username).exists():
            return Response({"error": "Username already exists."}, status=400)
        
        user = User.objects.create_user(username=username, email=email, password=password)
        
        # Tạo JWT token ngay sau khi đăng ký
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        
        return Response({
            "message": "Registration successful.",
            "username": username,
            "access_token": access_token,
            "refresh_token": str(refresh),
        })
        
class UserInfoAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        return Response({
            "username": user.username,
            "email": user.email,
            "last_login": user.last_login,
        }, status=status.HTTP_200_OK)
    

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)

        # Lấy thông tin user từ validated_data
        user = self.user

        # Thêm thông tin user vào response
        data.update({
            "username": user.username,
            "email": user.email,
            "last_login": user.last_login,
        })

        return data


# Custom view
class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer