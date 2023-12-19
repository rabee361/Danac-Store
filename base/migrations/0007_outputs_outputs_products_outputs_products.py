# Generated by Django 5.0 on 2023-12-18 17:03

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0006_medium'),
    ]

    operations = [
        migrations.CreateModel(
            name='Outputs',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('verify_code', models.IntegerField()),
                ('phonenumber', models.CharField(default='1212231243', max_length=30)),
                ('recive_pyement', models.FloatField()),
                ('discount', models.FloatField()),
                ('Reclaimed_products', models.FloatField()),
                ('previous_depts', models.FloatField()),
                ('remaining_amount', models.FloatField()),
                ('client', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='base.client')),
                ('employee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='base.employee')),
            ],
        ),
        migrations.CreateModel(
            name='Outputs_Products',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.IntegerField()),
                ('discount', models.FloatField()),
                ('output', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='base.outputs')),
                ('products', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='base.product')),
            ],
        ),
        migrations.AddField(
            model_name='outputs',
            name='products',
            field=models.ManyToManyField(through='base.Outputs_Products', to='base.product'),
        ),
    ]
