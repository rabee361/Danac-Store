# Generated by Django 4.2.10 on 2024-02-15 22:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Receipts', '0006_alter_incoming_day'),
    ]

    operations = [
        migrations.AlterField(
            model_name='incoming',
            name='number',
            field=models.IntegerField(),
        ),
    ]
