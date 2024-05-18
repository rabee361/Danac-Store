# Generated by Django 5.0 on 2024-05-14 18:23

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Clients_and_Products', '0037_alter_client_phonenumber_alter_client_phonenumber2'),
    ]

    operations = [
        migrations.AlterField(
            model_name='client',
            name='phonenumber2',
            field=models.CharField(blank=True, max_length=30, null=True, unique=True, validators=[django.core.validators.RegexValidator(regex='^(05|06|07)\\d{7 }$')]),
        ),
    ]