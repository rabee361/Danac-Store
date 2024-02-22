# Generated by Django 5.0 on 2024-02-17 09:36

import base.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Receipts', '0007_alter_incoming_barcode'),
    ]

    operations = [
        migrations.AlterField(
            model_name='manualreceipt',
            name='barcode',
            field=models.CharField(default=base.models.generate_barcode, editable=False, max_length=200),
        ),
        migrations.AlterField(
            model_name='output',
            name='barcode',
            field=models.CharField(default=base.models.generate_barcode, editable=False, max_length=200),
        ),
    ]