# Generated by Django 5.0 on 2024-03-04 12:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Clients_and_Products', '0028_alter_client_options'),
    ]

    operations = [
        migrations.AlterField(
            model_name='client',
            name='notes',
            field=models.TextField(blank=True, default='_', max_length=150, null=True),
        ),
    ]
