# Generated by Django 5.0 on 2024-01-11 05:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Clients_and_Products', '0002_alter_client_category'),
    ]

    operations = [
        migrations.AddField(
            model_name='client',
            name='debts',
            field=models.FloatField(default=0.0),
        ),
    ]
