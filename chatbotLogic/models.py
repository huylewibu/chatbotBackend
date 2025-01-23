from django.db import models
from django.utils.timezone import now
import uuid

class Login(models.Model):
    username = models.CharField(max_length=150, unique=True)
    password = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.username

class ChatInfo(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255, default="New Chat")  
    new_title = models.CharField(max_length=255, null=True, blank=True)
    username = models.CharField(max_length=50)
    created_at = models.DateTimeField(default=now)
    updated_at = models.DateTimeField(default=now)

    def __str__(self):
        return f"{self.title} by {self.username}"
    
class ChatMessage(models.Model):
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
    message_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)

    def __str__(self):
        return f"Message {self.id} in Chat {self.chat.title}"