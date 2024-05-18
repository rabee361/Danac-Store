# Generated by Django 5.0 on 2024-05-14 18:21

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Clients_and_Products', '0036_alter_order_product_total_points_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='client',
            name='phonenumber',
            field=models.CharField(max_length=30, unique=True, validators=[django.core.validators.RegexValidator(regex='^(05|06|07)\\d{7 }$')]),
        ),
        migrations.AlterField(
            model_name='client',
            name='phonenumber2',
            field=models.CharField(max_length=30, unique=True, validators=[django.core.validators.RegexValidator(regex='^(05|06|07)\\d{7 }$')],null=True,blank=True),
            preserve_default=False,
        ),
    ]