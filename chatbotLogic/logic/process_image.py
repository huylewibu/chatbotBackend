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
        
        # Kiểm tra nếu image_data là mảng
        if isinstance(image_data, list):
            # Tạo danh sách các phần tử đầu vào cho mô hình
            inputs = []
            for img in image_data:
                if "image/png" in img:
                    mime_type = "image/png"
                elif "image/jpeg" in img or "image/jpg" in img:
                    mime_type = "image/jpeg"
                else:
                    return {"bot_response": "Định dạng ảnh không hỗ trợ."}

                # Tách phần Base64
                image_data_format = img.split(",")[1]
                missing_padding = len(image_data_format) % 4
                if missing_padding:
                    image_data_format += "=" * (4 - missing_padding)
                image_bytes = base64.b64decode(image_data_format)

                # Thêm vào danh sách đầu vào
                inputs.append({'mime_type': mime_type, 'data': image_bytes})

            # Gửi yêu cầu phân tích tất cả ảnh cùng lúc
            response = model.generate_content(inputs + [prompt])
            description = response.text.strip()
            return {"bot_response": description}
        else:
            return {"bot_response": "Không nhận được dữ liệu ảnh hợp lệ."}

    except Exception as e:
        print(f"Lỗi trong process_image: {e}")
        return {"bot_response": "Không thể phân tích ảnh."}