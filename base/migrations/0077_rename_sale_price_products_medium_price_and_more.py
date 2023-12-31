# Generated by Django 4.2.8 on 2023-12-31 13:17

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0076_alter_codeverivecation_expires_at'),
    ]

    operations = [
        migrations.RenameField(
            model_name='products_medium',
            old_name='sale_price',
            new_name='price',
        ),
        migrations.AlterField(
            model_name='codeverivecation',
            name='expires_at',
            field=models.DateTimeField(default=datetime.datetime(2023, 12, 31, 13, 27, 4, 694916, tzinfo=datetime.timezone.utc)),
        ),
    ]
