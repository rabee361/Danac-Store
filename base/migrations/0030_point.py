# Generated by Django 5.0 on 2023-12-15 17:27

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0029_userlocation'),
    ]

    operations = [
        migrations.CreateModel(
            name='Point',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.FloatField()),
                ('expire_date', models.DateField()),
                ('date', models.DateField(auto_now_add=True)),
                ('is_used', models.BooleanField(default=False)),
                ('client', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='base.client')),
            ],
        ),
    ]
