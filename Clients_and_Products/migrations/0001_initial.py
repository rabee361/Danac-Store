# Generated by Django 4.2.10 on 2024-02-15 21:49

import base.models
import django.contrib.gis.db.models.fields
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import phonenumber_field.modelfields
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Cart',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('barcode', models.CharField(default=uuid.uuid4, max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=35)),
                ('image', models.ImageField(default='images/category.webp', null=True, upload_to='images/categories')),
            ],
            options={
                'ordering': ['-id'],
            },
        ),
        migrations.CreateModel(
            name='Client',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=30)),
                ('address', models.CharField(max_length=100)),
                ('phonenumber', phonenumber_field.modelfields.PhoneNumberField(max_length=128, region='DZ')),
                ('category', models.CharField(choices=[('سوبرماركت', 'سوبرماركت'), ('مقهى', 'مقهى'), (' جملة', ' جملة'), (' نصف جملة', ' نصف جملة'), ('مطعم', 'مطعم'), ('تجزئة', 'تجزئة')], max_length=75)),
                ('notes', models.TextField(default='_', max_length=150)),
                ('location', django.contrib.gis.db.models.fields.PointField(null=True, srid=4326)),
                ('debts', models.FloatField(default=0.0, validators=[django.core.validators.MinValueValidator(0.0)])),
            ],
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('total', models.IntegerField()),
                ('total_points', models.IntegerField()),
                ('products_num', models.IntegerField(default=0)),
                ('created', models.DateField(auto_now_add=True)),
                ('delivery_date', models.DateField()),
                ('delivered', models.BooleanField(default=False, null=True)),
                ('barcode', models.CharField(max_length=200, null=True)),
                ('client', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Clients_and_Products.client')),
            ],
        ),
        migrations.CreateModel(
            name='ProductType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('image', models.ImageField(default='images/category.webp', null=True, upload_to='images/product_types')),
            ],
            options={
                'ordering': ['-id'],
            },
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('image', models.ImageField(blank=True, default='images/category.webp', null=True, upload_to='images/products')),
                ('description', models.TextField(blank=True, max_length=2000, null=True)),
                ('quantity', models.IntegerField()),
                ('purchasing_price', models.FloatField()),
                ('notes', models.TextField(blank=True, max_length=1000, null=True)),
                ('made_at', models.DateField(blank=True, null=True)),
                ('expires_at', models.DateField(blank=True, null=True)),
                ('limit_less', models.IntegerField()),
                ('limit_more', models.IntegerField()),
                ('num_per_item', models.IntegerField(blank=True, default=0)),
                ('item_per_carton', models.IntegerField(blank=True, default=0)),
                ('sale_price', models.IntegerField()),
                ('added', models.DateTimeField(auto_now_add=True)),
                ('barcode', models.CharField(blank=True, default=' ', max_length=200)),
                ('points', models.IntegerField()),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Clients_and_Products.category')),
            ],
            options={
                'ordering': ['-added'],
            },
        ),
        migrations.CreateModel(
            name='Points',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.FloatField()),
                ('expire_date', models.DateField(default=base.models.get_expiration_date)),
                ('date', models.DateField(auto_now_add=True)),
                ('is_used', models.BooleanField(default=False)),
                ('client', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Clients_and_Products.client')),
            ],
        ),
        migrations.CreateModel(
            name='Order_Product',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.IntegerField()),
                ('total_price', models.FloatField()),
                ('total_points', models.IntegerField()),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Clients_and_Products.order')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Clients_and_Products.product')),
            ],
        ),
        migrations.AddField(
            model_name='order',
            name='products',
            field=models.ManyToManyField(through='Clients_and_Products.Order_Product', to='Clients_and_Products.product'),
        ),
        migrations.AddField(
            model_name='category',
            name='product_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Clients_and_Products.producttype'),
        ),
        migrations.CreateModel(
            name='Cart_Products',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.IntegerField(default=1)),
                ('cart', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Clients_and_Products.cart')),
                ('products', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Clients_and_Products.product')),
            ],
            options={
                'ordering': ['products__added'],
            },
        ),
        migrations.AddField(
            model_name='cart',
            name='customer',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Clients_and_Products.client'),
        ),
        migrations.AddField(
            model_name='cart',
            name='items',
            field=models.ManyToManyField(through='Clients_and_Products.Cart_Products', to='Clients_and_Products.product'),
        ),
        migrations.CreateModel(
            name='Ad',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('image_ad', models.ImageField(upload_to='images/ads')),
                ('product', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='Clients_and_Products.product')),
            ],
        ),
    ]
