# Generated by Django 5.0 on 2023-12-26 09:08

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0042_customuser_is_accepted_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='codeverification',
            name='expires_at',
            field=models.DateTimeField(default=datetime.datetime(2023, 12, 26, 9, 18, 42, 586073, tzinfo=datetime.timezone.utc)),
        ),
    ]