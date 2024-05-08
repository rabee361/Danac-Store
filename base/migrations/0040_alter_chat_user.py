# Generated by Django 5.0 on 2024-04-22 12:43

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0039_customuser_get_notifications'),
    ]

    operations = [
        migrations.AlterField(
            model_name='chat',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
