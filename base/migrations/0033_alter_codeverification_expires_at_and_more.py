# Generated by Django 5.0 on 2023-12-24 18:37

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0032_alter_codeverification_created_at_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='codeverification',
            name='expires_at',
            field=models.DateField(default=datetime.datetime(2023, 12, 24, 18, 47, 5, 606948, tzinfo=datetime.timezone.utc)),
        ),
        migrations.AlterField(
            model_name='codeverivecation',
            name='expires_at',
            field=models.DateTimeField(default=datetime.datetime(2023, 12, 24, 18, 47, 5, 604949, tzinfo=datetime.timezone.utc)),
        ),
    ]
