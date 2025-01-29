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
from .models import ChatInfo, ChatMessage
from .utils import error_response

class ChatbotAPI(APIView):
    def post(self, request):
        user_input = request.data.get('message', '')
        chat_id = request.data.get('chat_id')
        chat_history = request.data.get('chat_history', [])


        if not user_input or not chat_id:
            return Response({"error": "Missing required fields"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Kiểm tra nếu chat_id tồn tại trong database
            chat_id = ChatInfo.objects.filter(id=chat_id).first()
            if not chat_id:
                # Nếu không tồn tại, trả về lỗi
                return Response({"error": "Chat not found"}, status=status.HTTP_404_NOT_FOUND)
            # Tạo tin nhắn của người dùng
            user_message = ChatMessage.objects.create(
                chat=chat_id,
                is_bot=False,
                message=user_input,
                sequence=len(chat_id.message.all()) + 1,  # Đếm số lượng tin nhắn
                created_at=now(),
            )
            
            # Xử lý phản hồi từ bot
            bot_response = generate_response(user_input, chat_history)
            if not bot_response:
                bot_response = "Không nhận được phản hồi từ bot."
            # Tạo tin nhắn phản hồi từ bot
            bot_message = ChatMessage.objects.create(
                chat=chat_id,
                is_bot=True,
                message=bot_response,
                sequence=user_message.sequence + 1,
                created_at=now(),
            )

            # Cập nhật thời gian cập nhật
            chat_id.updated_at = now()
            chat_id.save()

            # Trả về kết quả
            return Response({
                "user_message": {
                    "id": user_message.id,
                    "message": user_message.message,
                    "is_bot": user_message.is_bot,
                    "created_at": user_message.created_at,
                },
                "bot_response": {
                    "id": bot_message.id,
                    "message": bot_message.message,
                    "is_bot": bot_message.is_bot,
                    "created_at": bot_message.created_at,
                }
            }, status=status.HTTP_200_OK)

        except Exception as e:
            print(f"Error in ChatbotAPI: {e}")
            return error_response("BOT_PROCESSING_ERROR", "Lỗi xảy ra khi xử lý phản hồi từ bot.", status.HTTP_500_INTERNAL_SERVER_ERROR)


class AddChatAPI(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        username = request.user.username
        title = request.data.get('title', '')

        try:
            new_chat = ChatInfo.objects.create(
                username = username,
                title = title,
                created_at = now(),
                updated_at = now()
            )

            return Response(
                {
                    "message": "Chat created successfully",
                    "chat": {
                        "id": new_chat.id,
                        "title": new_chat.title,
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
            chats = ChatInfo.objects.filter(username=request.user.username).order_by("-updated_at")

            chats_data = [
                {
                    "id": chat.id,
                    "title": chat.title,
                    "updated_at": chat.updated_at,
                }
                for chat in chats
            ]
            return Response({"chats": chats_data}, status=status.HTTP_200_OK)
        except Exception as e:
            return error_response("LOAD_CHAT_ERROR", f"Failed to load chats: {str(e)}", status.HTTP_500_INTERNAL_SERVER_ERROR)

class GetMessagesByChatAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, chat_id):
        try:
            # Lấy đoạn chat dựa trên chat_id và username của user hiện tại
            chat = ChatInfo.objects.get(id=chat_id, username=request.user.username)

            # Lấy danh sách tin nhắn thuộc về đoạn chat
            messages = ChatMessage.objects.filter(chat_id=chat.id).order_by("sequence")

            # Chuyển đổi tin nhắn thành định dạng JSON
            message_data = [
                {
                    "id": message.id,
                    "message": message.message,
                    "is_bot": message.is_bot,
                    "sequence": message.sequence,
                    "created_at": message.created_at,
                }
                for message in messages
            ]

            # Trả về thông tin đoạn chat và danh sách tin nhắn
            return Response({
                "chat": {
                    "id": chat.id,
                    "title": chat.title,
                    "created_at": chat.created_at,
                    "updated_at": chat.updated_at,
                },
                "message_data": message_data,
            }, status=status.HTTP_200_OK)

        except ChatInfo.DoesNotExist:
            return Response({"error": "Chat not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return error_response("LOAD_MESSAGES_ERROR", f"Failed to load messages: {str(e)}", status.HTTP_500_INTERNAL_SERVER_ERROR)

class RenameChatAPI(APIView):
    def post(self, request):
        user_input = request.data.get('message', '')
        chat_id = request.data.get('chat_id')

        if not user_input:
            return Response({"error": "No input provided"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            chat_name = generate_chat_name(user_input)

            rows_updated = ChatInfo.objects.filter(id=chat_id).update(
                title=chat_name,
            )
            # Kiểm tra xem có bản ghi nào được cập nhật không
            if rows_updated == 0:
                return Response({"error": "Chat not found"}, status=status.HTTP_404_NOT_FOUND)
            return Response({"chat_name": chat_name}, status=status.HTTP_200_OK)

        except Exception as e:
            print(f"Error in RenameChatAPI: {e}")
            return error_response(
                "RENAME_CHAT_ERROR",
                "Failed to rename chat.",
                status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
    
class UpdateMessageAPI(APIView):
    def post(self, request):
        chat_id = request.data.get("chat_id", "")
        message_id = request.data.get("message_id", "")
        new_text = request.data.get("new_text", "")
        chat_history = request.data.get("chat_history", [])

        if not new_text:
            return Response({"error": "No input provided"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user_message = ChatMessage.objects.get(chat_id=chat_id, id=message_id, is_bot=False)
            user_message.message = new_text
            user_message.save()
            print("user_message: ", user_message)
        except ChatMessage.DoesNotExist:
            return Response({"error": "Message not found"}, status=status.HTTP_404_NOT_FOUND)

        # Xử lý logic chatbot
        try:
            # Gửi câu hỏi đã chỉnh sửa đến bot
            bot_response = generate_response(new_text, chat_history)
            if not bot_response:
                bot_response = "Không nhận được phản hồi từ bot."  # Đáp ứng mặc định nếu không có kết quả
        
            try:
                bot_message = ChatMessage.objects.get(chat_id=chat_id, sequence=user_message.sequence + 1, is_bot=True)
                bot_message.message = bot_response 
                print("bot_message: ", bot_message)
                bot_message.save()
            except ChatMessage.DoesNotExist:
                return Response({"error": "Bot message not found"}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            print(f"Error in generate_response: {e}")
            return error_response("BOT_PROCESSING_ERROR", "Lỗi xảy ra khi xử lý phản hồi từ bot.", status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Trả về phản hồi mới từ bot
        return Response({
            "message_id": message_id,
            "new_text": new_text,
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