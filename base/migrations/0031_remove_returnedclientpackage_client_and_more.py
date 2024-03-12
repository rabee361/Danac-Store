# Generated by Django 5.0 on 2024-03-08 08:30

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Clients_and_Products', '0029_alter_client_notes'),
        ('base', '0030_remove_returnedgoodsclient_client_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='returnedclientpackage',
            name='client',
        ),
        migrations.RemoveField(
            model_name='returnedsupplierpackage',
            name='supplier',
        ),
        migrations.AddField(
            model_name='returnedgoodsclient',
            name='client',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='Clients_and_Products.client'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='returnedgoodssupplier',
            name='supplier',
            field=models.ForeignKey(default=3, on_delete=django.db.models.deletion.CASCADE, to='base.supplier'),
            preserve_default=False,
        ),
    ]