# Generated by Django 5.1.4 on 2025-01-23 09:02

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chatbotLogic', '0005_alter_chatinfo_id_alter_chatmessage_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='chatmessage',
            name='chat',
            field=models.ForeignKey(db_column='chat_id', on_delete=django.db.models.deletion.CASCADE, related_name='message', to='chatbotLogic.chatinfo'),
        ),
    ]
