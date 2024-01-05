# Generated by Django 5.0 on 2024-01-05 06:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0003_alter_customuser_image_alter_product_barcode'),
    ]

    operations = [
        migrations.AlterField(
            model_name='incoming',
            name='Reclaimed_products',
            field=models.FloatField(blank=True, default=0.0),
        ),
        migrations.AlterField(
            model_name='incoming',
            name='discount',
            field=models.FloatField(blank=True, default=0.0),
        ),
        migrations.AlterField(
            model_name='incoming',
            name='previous_depts',
            field=models.FloatField(blank=True, default=0.0),
        ),
        migrations.AlterField(
            model_name='incoming',
            name='remaining_amount',
            field=models.FloatField(blank=True, default=0.0),
        ),
        migrations.AlterField(
            model_name='manualreceipt',
            name='previous_depts',
            field=models.FloatField(blank=True, default=0.0),
        ),
        migrations.AlterField(
            model_name='manualreceipt',
            name='reclaimed_products',
            field=models.FloatField(blank=True, default=0.0),
        ),
        migrations.AlterField(
            model_name='manualreceipt',
            name='remaining_amount',
            field=models.FloatField(blank=True, default=0.0),
        ),
        migrations.AlterField(
            model_name='output',
            name='Reclaimed_products',
            field=models.FloatField(blank=True, default=0.0),
        ),
        migrations.AlterField(
            model_name='output',
            name='discount',
            field=models.FloatField(blank=True, default=0.0),
        ),
        migrations.AlterField(
            model_name='output',
            name='previous_depts',
            field=models.FloatField(blank=True, default=0.0),
        ),
        migrations.AlterField(
            model_name='output',
            name='remaining_amount',
            field=models.FloatField(blank=True, default=0.0),
        ),
    ]
