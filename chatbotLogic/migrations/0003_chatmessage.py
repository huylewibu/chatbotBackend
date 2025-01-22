# Generated by Django 5.1.4 on 2025-01-22 11:17

import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chatbotLogic', '0002_chatinfo'),
    ]

    operations = [
        migrations.CreateModel(
            name='ChatMessage',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('is_bot', models.BooleanField(default=False)),
                ('message', models.TextField()),
                ('sequence', models.IntegerField()),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('chat', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='message', to='chatbotLogic.chatinfo')),
            ],
        ),
    ]
