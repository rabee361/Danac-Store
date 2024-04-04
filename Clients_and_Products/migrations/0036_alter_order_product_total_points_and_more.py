# Generated by Django 5.0 on 2024-04-03 10:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Clients_and_Products', '0035_alter_client_address_alter_client_store_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order_product',
            name='total_points',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='producttype',
            name='name',
            field=models.CharField(max_length=50, unique=True),
        ),
    ]