# Generated by Django 5.0 on 2024-02-15 15:17

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Clients_and_Products', '0017_order_total_price'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='order',
            name='products_num',
        ),
        migrations.RemoveField(
            model_name='order',
            name='total_points',
        ),
        migrations.RemoveField(
            model_name='order',
            name='total_price',
        ),
    ]
