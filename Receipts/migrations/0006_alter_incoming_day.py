# Generated by Django 4.2.10 on 2024-02-15 22:24

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0001_initial'),
        ('Receipts', '0005_alter_incoming_day'),
    ]

    operations = [
        migrations.AlterField(
            model_name='incoming',
            name='day',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='base.day'),
        ),
    ]
