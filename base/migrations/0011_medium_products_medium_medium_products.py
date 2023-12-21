# Generated by Django 5.0 on 2023-12-20 20:23

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0010_remove_incoming_products_incoming_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Medium',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.CreateModel(
            name='Products_Medium',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('discount', models.FloatField(default=0)),
                ('num_item', models.IntegerField(default=0)),
                ('total_price', models.FloatField(default=0)),
                ('medium', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='base.medium')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='base.product')),
            ],
        ),
        migrations.AddField(
            model_name='medium',
            name='products',
            field=models.ManyToManyField(through='base.Products_Medium', to='base.product'),
        ),
    ]
