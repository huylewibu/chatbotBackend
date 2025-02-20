from django.db import models
from django.utils.timezone import now
import uuid
from psqlextra.models import PostgresPartitionedModel
from django.db import models
from django.utils import timezone
import random

class Login(models.Model):
    username = models.CharField(max_length=150, unique=True)
    password = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.username

class ChatInfo(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255, default="New Chat")  
    username = models.CharField(max_length=50)
    created_at = models.DateTimeField(default=now)
    updated_at = models.DateTimeField(default=now)

    def __str__(self):
        return f"{self.title} by {self.username}"
    
class ChatMessage(PostgresPartitionedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    chat = models.ForeignKey(
        ChatInfo, 
        on_delete=models.CASCADE,
        related_name="message",
        db_column="chat_id",
    )
    is_bot = models.BooleanField(default=False)
    message = models.TextField()
    sequence = models.IntegerField()
    created_at = models.DateTimeField(default=now)
    is_has_image = models.BooleanField(default=False)
    image_url = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Message {self.id} in Chat {self.chat.title}"
    
class OTPRegister(models.Model):
    user_email = models.EmailField()
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    def is_expired(self):
        return timezone.now() > self.expires_at

    @staticmethod
    def generate_code():
        return str(random.randint(100000, 999999))