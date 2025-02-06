# import google.generativeai as genai
from google import genai
import os
import base64
from dotenv import load_dotenv
# from google.generativeai import types
from google.genai import types

load_dotenv()

API_KEY = os.getenv("GOOGLE_API_KEY")
client = genai.Client(api_key=API_KEY)

# client = genai.GenerativeModel("imagen-3.0-generate-002")

def generate_image_prompt(prompt, number_images = 1,):
    try:
        images_base64 = []
        response = client.models.generate_images(
            model="imagen-3.0-generate-001",
            prompt=prompt,
            config=types.GenerateImagesConfig(
                number_of_images=number_images,
                include_rai_reason=True,
                output_mime_type="image/png",
            )
        )

        if response and response.parts:
            for image_data in response.parts:
                if isinstance(image_data, bytes):
                    image_base64 = base64.b64encode(image_data).decode("utf-8")
                    images_base64.append(f"data:image/jpeg;base64,{image_base64}")
        if images_base64:
            return {"images": images_base64}
        return {"error": "Không nhận được ảnh từ AI."}

    except Exception as e:
        print(f"Lỗi trong generate_image_prompt: {e}")
        return {"error": "Lỗi xảy ra trong quá trình tạo ảnh từ AI."}




