# Generated by Django 5.0 on 2023-12-15 16:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0027_alter_client_location'),
    ]

    operations = [
        migrations.AddField(
            model_name='client',
            name='notes',
            field=models.TextField(default='note', max_length=150),
        ),
    ]
