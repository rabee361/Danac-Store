# Generated by Django 5.0 on 2024-09-15 18:32

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Clients_and_Products', '0041_alter_order_options'),
        ('base', '0058_rename_product_order_envoy_driverorderproduct_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='returnedclientpackage',
            name='client',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='Clients_and_Products.client'),
        ),
        migrations.AddField(
            model_name='returnedsupplierpackage',
            name='supplier',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='base.supplier'),
        ),
    ]
