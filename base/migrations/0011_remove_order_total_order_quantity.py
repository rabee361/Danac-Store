# Generated by Django 5.0 on 2023-12-18 20:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0010_order_order_products_order_products'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='order',
            name='total',
        ),
        migrations.AddField(
            model_name='order',
            name='quantity',
            field=models.IntegerField(default=0),
        ),
    ]
