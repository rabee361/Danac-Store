# Generated by Django 5.0 on 2023-12-19 23:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='debt_client',
            name='date',
            field=models.DateField(auto_now_add=True),
        ),
    ]