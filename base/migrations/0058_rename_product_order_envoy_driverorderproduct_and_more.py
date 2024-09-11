# Generated by Django 5.0 on 2024-06-20 09:53

import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Clients_and_Products', '0041_alter_order_options'),
        ('base', '0057_alter_customuser_phonenumber'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Product_Order_Envoy',
            new_name='DriverOrderProduct',
        ),
        migrations.CreateModel(
            name='DriverOrder',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('client', models.CharField(max_length=50)),
                ('address', models.CharField(default='address', max_length=100)),
                ('phonenumber', models.CharField(max_length=30, validators=[django.core.validators.RegexValidator(regex='^(05|06|07)\\d{8}$')])),
                ('products_num', models.IntegerField(default=0)),
                ('total_price', models.FloatField(default=0)),
                ('created', models.DateField(auto_now_add=True)),
                ('delivery_date', models.DateField()),
                ('delivered', models.BooleanField(default=False, null=True)),
                ('products', models.ManyToManyField(through='base.DriverOrderProduct', to='Clients_and_Products.product')),
            ],
        ),
        migrations.AlterField(
            model_name='driverorderproduct',
            name='order_envoy',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='base.driverorder'),
        ),
        migrations.DeleteModel(
            name='OrderEnvoy',
        ),
    ]