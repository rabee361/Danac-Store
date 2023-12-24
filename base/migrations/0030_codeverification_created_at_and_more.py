# Generated by Django 5.0 on 2023-12-24 18:32

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0029_mediumtwo_orderenvoy_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='codeverification',
            name='created_at',
            field=models.DateField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name='codeverification',
            name='expires_at',
            field=models.DateField(default=datetime.datetime(2023, 12, 24, 18, 42, 22, 841652, tzinfo=datetime.timezone.utc)),
        ),
        migrations.AlterField(
            model_name='codeverivecation',
            name='expires_at',
            field=models.DateTimeField(default=datetime.datetime(2023, 12, 24, 18, 42, 22, 837649, tzinfo=datetime.timezone.utc)),
        ),
    ]
