import base64
import httpx
from PIL import Image
from io import BytesIO
import os
import google.generativeai as genai

API_KEY = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=API_KEY)

def process_image(image_data, prompt="Mô tả nội dung của bức ảnh này."):
    try:
        # Khởi tạo mô hình Gemini
        model = genai.GenerativeModel(model_name="gemini-2.0-flash-thinking-exp-01-21")

        if "image/png" in image_data:
            mime_type = "image/png"
        elif "image/jpeg" in image_data or "image/jpg" in image_data:
            mime_type = "image/jpeg"
        else:
            return {"bot_response": "Định dạng ảnh không hỗ trợ."}
        
        image_data_format = image_data.split(",")[1] 
        missing_padding = len(image_data_format) % 4
        if missing_padding:
            image_data_format += "=" * (4 - missing_padding)
        image_bytes = base64.b64decode(image_data_format)

        response = model.generate_content([
            {'mime_type': mime_type, 'data': image_bytes},
            prompt
        ])

        description = response.text.strip()
        return {
            "bot_response": description
        }

    except Exception as e:
        print(f"Lỗi trong process_image: {e}")
        return {
            "bot_response": "Không thể phân tích ảnh."
        }