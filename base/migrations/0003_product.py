# Generated by Django 5.0 on 2023-12-13 02:08

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0002_alter_customuser_managers_delete_product'),
    ]

    operations = [
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('iamge', models.ImageField(upload_to='images/poduct')),
                ('description', models.TextField(max_length=2000)),
                ('quantity', models.IntegerField()),
                ('purchasing_price', models.FloatField()),
                ('num_per_item', models.IntegerField()),
                ('item_per_carton', models.IntegerField()),
                ('limit', models.IntegerField()),
                ('info', models.TextField(max_length=1000)),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='base.category')),
            ],
        ),
    ]