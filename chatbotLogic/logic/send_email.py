from django.core.mail import send_mail
from django.conf import settings
import re
import logging

logger = logging.getLogger(__name__)


def is_valid_email(email):
    return re.match(r"[^@]+@[^@]+\.[^@]+", email)

def send_otp_email(email, otp_code):
    subject = "Xác nhận đăng ký tài khoản"
    message = f"Mã OTP của bạn là: {otp_code}. Mã này sẽ hết hạn sau 5 phút."
    from_email = settings.EMAIL_HOST_USER
    recipient_list = [email]
    print("send_otp_email: ", email)
    print("from email: ", from_email)
    print("recipient_list: ", recipient_list)
    try:
        send_mail(subject, message, from_email, recipient_list)
        logger.info("Email sent successfully")
    except Exception as e:
        logger.error(f"Failed to send email: {e}")
        print(f"SMTP ERROR: {e}")
        raise Exception(f"Failed to send email: {e}")