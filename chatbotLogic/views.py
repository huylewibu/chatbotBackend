from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .logic.chatbot import generate_response, generate_chat_name
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.utils.timezone import now
from .models import ChatInfo
from .utils import error_response

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
            return error_response("BOT_PROCESSING_ERROR", "Lỗi xảy ra khi xử lý phản hồi từ bot.", status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response({"user_message": user_input, "bot_response": bot_response})

class AddChatAPI(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        username = request.user.username
        title = request.data.get('title', 'New Chat')

        try:
            new_chat = ChatInfo.objects.create(
                username = username,
                title = title,
                new_title=None,
                created_at = now(),
                updated_at = now()
            )

            return Response(
                {
                    "message": "Chat created successfully",
                    "chat": {
                        "id": new_chat.id,
                        "title": new_chat.title,
                        "new_title": new_chat.new_title,
                        "username": new_chat.username,
                        "created_at": new_chat.created_at,
                        "updated_at": new_chat.updated_at,
                    },
                },
                status=status.HTTP_201_CREATED
            )
        except Exception as e:
            return error_response("CREATE_CHAT_ERROR", f"Failed to create chat: {str(e)}", status.HTTP_500_INTERNAL_SERVER_ERROR)

class GetChatsAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            username = request.user.username
            chats = ChatInfo.objects.filter(username=username).order_by("-updated_at")
            data = []

            for chat in chats:
                messages = chat.chatmessage_set.all().order_by("created_at")
                chat_data = {
                    "id": chat.id,
                    "title": chat.title,
                    "messages": [
                        {
                            "id": message.id,
                            "message": message.message,
                            "is_bot": message.is_bot,
                            "created_at": message.created_at,
                        }
                        for message in messages
                    ],
                    "created_at": chat.created_at,
                    "updated_at": chat.updated_at,
                }
                data.append(chat_data)

            return Response({"chats": data}, status=status.HTTP_200_OK)
        except Exception as e:
            return error_response("LOAD_CHAT_ERROR", f"Failed to load chats: {str(e)}", status.HTTP_500_INTERNAL_SERVER_ERROR)


class RenameChatAPI(APIView):
    def post(self, request):
        user_input = request.data.get('message', '')
        chat_id = request.data.get('chat_id')
        print("chat_id: ", chat_id)
        if not user_input:
            return Response({"error": "No input provided"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Gọi hàm generate_chat_name
            chat_name = generate_chat_name(user_input)
            if chat_id:
                chat = ChatInfo.objects.get(id=chat_id, username=request.user.username)
                print("chat: ", chat)
                chat.new_title = chat_name
                chat.save()
        except Exception as e:
            print(f"Error in generate_chat_name: {e}")
            return error_response("RENAME_CHAT_ERROR", "Failed to generate chat name.", status.HTTP_500_INTERNAL_SERVER_ERROR)
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
            return error_response("BOT_PROCESSING_ERROR", "Lỗi xảy ra khi xử lý phản hồi từ bot.", status.HTTP_500_INTERNAL_SERVER_ERROR)

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
        
        try:
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
        except Exception as e:
            return error_response("REGISTER_ERROR", f"Failed to register: {str(e)}", status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class UserInfoAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            user = request.user
            return Response({
                "username": user.username,
                "email": user.email,
                "last_login": user.last_login,
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return error_response("FETCH_USER_INFO_ERROR", f"Failed to fetch user info: {str(e)}", status.HTTP_500_INTERNAL_SERVER_ERROR)
    
class RemoveChatApi(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, chat_id):
        try:
            chat = ChatInfo.objects.get(id=chat_id, username=request.user.username)
            chat.delete()
            return Response({"message": "Chat removed successfully."}, status=status.HTTP_200_OK)
        except ChatInfo.DoesNotExist:
            return error_response("CHAT_NOT_FOUND", "Chat not found.", status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return error_response("DELETE_CHAT_ERROR", f"Failed to delete chat: {str(e)}", status.HTTP_500_INTERNAL_SERVER_ERROR)
    

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