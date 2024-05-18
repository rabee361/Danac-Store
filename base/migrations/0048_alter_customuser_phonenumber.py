# Generated by Django 5.0 on 2024-05-14 19:12

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0047_alter_customuser_phonenumber_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='phonenumber',
            field=models.CharField(max_length=30, unique=True, validators=[django.core.validators.RegexValidator(regex='^(05|06|07)\\d{7}$')]),
        ),
    ]