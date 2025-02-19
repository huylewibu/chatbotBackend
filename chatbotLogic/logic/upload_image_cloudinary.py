import httpx
import os

def upload_image_to_cloudinary(image_base64_list):
    try:
        CLOUDINARY_URL = f"https://api.cloudinary.com/v1_1/{os.getenv('CLOUDINARY_CLOUD_NAME')}/image/upload"
        UPLOAD_PRESET = os.getenv("CLOUDINARY_UPLOAD_PRESET")

        image_urls = []  # Danh sách URL ảnh đã upload

        for image_base64 in image_base64_list:  # Duyệt từng ảnh trong danh sách
            # Gửi request lên Cloudinary
            response = httpx.post(
                CLOUDINARY_URL,
                data={"file": image_base64, "upload_preset": UPLOAD_PRESET},
                timeout=30.0
            )

            # Kiểm tra nếu thành công
            if response.status_code == 200:
                result = response.json()
                image_urls.append(result["secure_url"])
            else:
                print(f"❌ Lỗi khi upload ảnh ({response.status_code}): {response.text}")

        return image_urls  # Trả về danh sách URL ảnh đã upload

    except httpx.TimeoutException:
        print("⚠️ Lỗi: Request tới Cloudinary bị timeout.")
        return []
    except Exception as e:
        print(f"⚠️ Lỗi upload Cloudinary: {e}")
        return []
