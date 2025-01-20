from .gemini import chat_logic

def generate_response(user_input, chat_history):
    try:
        bot_response = chat_logic(user_input, chat_history)
        if isinstance(bot_response, dict):  # Kiểm tra nếu là object
            bot_response = bot_response.get("bot_response", "Lỗi không có phản hồi từ bot.")
        return bot_response
    except Exception as e:
        print(f"Error in chat_logic: {e}")
        return "Lỗi xảy ra khi xử lý phản hồi từ bot."
    
def generate_chat_name(prompt):
    try:
        # Gọi hàm chat_logic với `is_rename_prompt=True`
        result = chat_logic(prompt, is_rename_prompt=True)
        chat_name = result.get("bot_response", "Cuộc trò chuyện mới")
        return chat_name.strip()
    except Exception as e:
        print(f"Error in generate_chat_name: {e}")
        return "Cuộc trò chuyện mới" 