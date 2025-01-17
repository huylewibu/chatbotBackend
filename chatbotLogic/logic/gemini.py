import google.generativeai as genai
import os
from dotenv import load_dotenv
from openai import OpenAI
import gradio as gr

load_dotenv()

BASE_URL = os.getenv("BASE_URL")
API_KEY = os.getenv("GOOGLE_API_KEY")

# Cấu hình generation
generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 40,
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
# model = genai.GenerativeModel(
#         model_name="gemini-2.0-flash-exp",
#         generation_config=generation_config,
#         # system_instruction="This is a new chat, and user ask you. No rely and comment just answer for this chat, Max length is 20 characters and Vietnamese name is preferred"
#     )
client = OpenAI(
    base_url=BASE_URL,
    api_key=API_KEY
)

def chat_logic(message, chat_history=[], is_rename_prompt=False):
    try:
        messages = [{"role": "user", "content": msg["content"]} for msg in chat_history]
        messages.append({"role": "user", "content": message})
        
        if is_rename_prompt:
            system_instruction = (
                f"This is a new chat, and user asked: {message}. "
                "Provide a suitable name for the chat. No reply or comment, "
                "just the name in maximum 20 characters, and Vietnamese preferred."
            )
            prompt = system_instruction.format(content=message)
            messages.append({"role": "system", "content": prompt})
            
        chat_completion = client.chat.completions.create(
            model="gemma2-9b-it",
            messages=messages,
            stream=False,
        )

        bot_response = chat_completion.choices[0].message.content.strip()
        return {"bot_response": bot_response}
    except Exception as e:
        print("Error:", str(e))
        return {"bot_response": "Lỗi xảy ra trong quá trình xử lý."}


