import google.generativeai as genai
import os
import absl.logging
from dotenv import load_dotenv
# import openai

absl.logging.set_verbosity(absl.logging.ERROR)

load_dotenv()

BASE_URL = os.getenv("BASE_URL")
API_KEY = os.getenv("GOOGLE_API_KEY")

genai.configure(api_key=API_KEY)

# Cấu hình generation
generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain"
}

# Cấu hình safety settings
safety_settings = [
    {
        "category": "HARM_CATEGORY_HARASSMENT",
        "threshold": "BLOCK_LOW_AND_ABOVE",
    },
    {
        "category": "HARM_CATEGORY_HATE_SPEECH",
        "threshold": "BLOCK_LOW_AND_ABOVE",
    },
]

model = genai.GenerativeModel(
    model_name="gemini-exp-1206",
    generation_config=generation_config,
    safety_settings=safety_settings,
)

def chat_logic(message, chat_history=[], is_rename_prompt=False):
    try:
        gemini_chat_history = [
            {"role": "user" if msg["role"] == "user" else "model", "parts": [msg["content"]]}
            for msg in chat_history
        ]

        gemini_chat_history.append({"role": "user", "parts": [message]})
        
        if is_rename_prompt:
            system_prompt  = (
                f"This is a new chat, and user asked: '{message}'. "
                "Based on this initial message, suggest a concise and relevant title for the chat. "
                "The title should reflect the likely topic or theme of the conversation, "
                "be in the same language as the user's message, and be no longer than 20 characters. "
                "Only provide the title, no other text or explanation."
            )
            gemini_chat_history.append({"role": "user", "parts": [system_prompt]})
            
        chat_session = model.start_chat(history=gemini_chat_history)
        response = chat_session.send_message(message)
        return {"bot_response": response.text.strip()}
    except Exception as e:
        print("Error:", str(e))
        return {"bot_response": "Lỗi xảy ra trong quá trình xử lý."}
