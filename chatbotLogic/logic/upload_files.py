import google.generativeai as genai
import os
import mimetypes
from dotenv import load_dotenv

# Load API key từ .env
load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY")

# Cấu hình Gemini API
genai.configure(api_key=API_KEY)

# Cấu hình model
generation_config = {
    "temperature": 0.7,
    "top_p": 0.9,
    "top_k": 40,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain"
}

model = genai.GenerativeModel(
    model_name="gemini-1.5-pro",
    generation_config=generation_config,
)

def process_document(file_path, query):
    print("file_path: ", file_path)
    print("query: ", query)
    try:
        # Xác định loại file
        mime_type, _ = mimetypes.guess_type(file_path)
        if not mime_type:
            mime_type = "application/octet-stream"

        # Đọc nội dung file
        with open(file_path, "rb") as f:
            document_content = f.read()

        # Gửi đến Gemini API để phân tích nội dung tài liệu
        response = model.generate_content([
            {
                "role": "user",  
                "parts": [
                    {
                        "mime_type": mime_type,
                        "data": document_content
                    }
                ]
            },
            {
                "role": "user", 
                "parts": [
                    {
                        "text": f"Trả lời câu hỏi dựa trên tài liệu: {query}"
                    }
                ]
            }
        ])
        print("Gemini API Response:", response)

        # Xử lý phản hồi từ Gemini API
        if hasattr(response, "text"):
            return response.text.strip()
        elif hasattr(response, "candidates") and len(response.candidates) > 0:
            return response.candidates[0].content.parts[0].text.strip()
        else:
            return "Không tìm thấy thông tin phù hợp trong tài liệu."

    except Exception as e:
        print("Error processing document:", str(e))
        return "Lỗi xảy ra trong quá trình xử lý tài liệu."
