# Generated by Django 5.0 on 2024-01-13 16:26

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Receipts', '0008_alter_output_products_options_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='output',
            old_name='product',
            new_name='products',
        ),
    ]
