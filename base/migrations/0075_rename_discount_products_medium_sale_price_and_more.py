# Generated by Django 4.2.8 on 2023-12-31 09:23

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0074_remove_salesemployee_representative_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='products_medium',
            old_name='discount',
            new_name='sale_price',
        ),
        migrations.RemoveField(
            model_name='manualreceipt',
            name='discount',
        ),
        migrations.AlterField(
            model_name='codeverivecation',
            name='expires_at',
            field=models.DateTimeField(default=datetime.datetime(2023, 12, 31, 9, 33, 26, 352424, tzinfo=datetime.timezone.utc)),
        ),
    ]
