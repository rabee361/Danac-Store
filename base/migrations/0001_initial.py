# Generated by Django 5.0 on 2023-12-16 12:13

import django.contrib.auth.models
import django.core.validators
import django.db.models.deletion
import django.utils.timezone
import phonenumber_field.modelfields
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Client',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=30)),
                ('address', models.CharField(max_length=100)),
                ('category', models.CharField(choices=[('سوبر ماركت', 'سوبر ماركت'), ('مقهى', 'مقهى'), ('محل جملة', 'محل جملة'), ('محل نصف جملة', 'محل نصف جملة')], max_length=75, null=True)),
                ('phomnenumber', phonenumber_field.modelfields.PhoneNumberField(max_length=128, region='DZ')),
                ('info', models.TextField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Department',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=30)),
            ],
        ),
        migrations.CreateModel(
            name='Employee',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=30)),
                ('breath_date', models.DateField()),
                ('phonenumber', phonenumber_field.modelfields.PhoneNumberField(max_length=128, region='DZ')),
                ('type_employee', models.CharField(max_length=20)),
                ('number_track', models.IntegerField()),
                ('salery', models.FloatField()),
                ('sale_perce', models.FloatField()),
                ('address', models.CharField(max_length=100)),
                ('info', models.TextField(max_length=1000)),
                ('date', models.DateField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Notifications',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.CreateModel(
            name='Supplier',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=30)),
                ('company', models.CharField(max_length=50)),
                ('phonenubmer', phonenumber_field.modelfields.PhoneNumberField(max_length=128, region='DZ')),
                ('address', models.CharField(max_length=100)),
                ('info', models.TextField(max_length=500)),
            ],
        ),
        migrations.CreateModel(
            name='CustomUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('phonenumber', phonenumber_field.modelfields.PhoneNumberField(max_length=128, region='DZ', unique=True)),
                ('username', models.CharField(max_length=200)),
                ('is_verified', models.BooleanField(default=False)),
                ('image', models.ImageField(null=True, upload_to='images/users')),
                ('address', models.CharField(default='one', max_length=100)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Cart',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='base.client')),
            ],
        ),
        migrations.CreateModel(
            name='CodeVerivecation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.IntegerField(validators=[django.core.validators.MinValueValidator(1000, 9999)])),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Driver',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('driver', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Discount',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('reason_discount', models.CharField(max_length=100)),
                ('total', models.FloatField()),
                ('date', models.DateField(auto_now_add=True)),
                ('employee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='base.employee')),
            ],
        ),
        migrations.CreateModel(
            name='Award',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('reason_award', models.CharField(max_length=100)),
                ('total', models.FloatField()),
                ('date', models.DateField(auto_now_add=True)),
                ('employee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='base.employee')),
            ],
        ),
        migrations.CreateModel(
            name='Advance',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('reason_advance', models.CharField(max_length=100)),
                ('total', models.FloatField()),
                ('date', models.DateField(auto_now_add=True)),
                ('employee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='base.employee')),
            ],
        ),
        migrations.CreateModel(
            name='Absence',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('num_absence', models.IntegerField()),
                ('amoumt_deducted', models.FloatField()),
                ('date', models.DateField(auto_now_add=True)),
                ('employee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='base.employee')),
            ],
        ),
        migrations.CreateModel(
            name='Expense',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('reason_expense', models.CharField(max_length=100)),
                ('total', models.FloatField()),
                ('date', models.DateField(auto_now_add=True)),
                ('employee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='base.employee')),
            ],
        ),
        migrations.CreateModel(
            name='Incoming',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('agent', models.CharField(max_length=30)),
                ('num_truck', models.IntegerField()),
                ('code_verefy', models.IntegerField()),
                ('recive_pyement', models.FloatField()),
                ('discount', models.FloatField()),
                ('previous_depts', models.FloatField()),
                ('employee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='base.employee')),
            ],
        ),
        migrations.CreateModel(
            name='OverTime',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('num_hours', models.FloatField()),
                ('deserved_amount', models.FloatField()),
                ('date', models.DateField(auto_now_add=True)),
                ('employee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='base.employee')),
            ],
        ),
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
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('iamge', models.ImageField(upload_to='images/product')),
                ('description', models.TextField(max_length=2000)),
                ('quantity', models.IntegerField()),
                ('purch_price', models.FloatField()),
                ('sale_price', models.IntegerField()),
                ('num_per_item', models.IntegerField()),
                ('item_per_carton', models.IntegerField()),
                ('limit', models.IntegerField()),
                ('info', models.TextField(max_length=1000)),
                ('added', models.DateTimeField(auto_now_add=True)),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='base.category')),
            ],
            options={
                'ordering': ['-added'],
            },
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('total', models.IntegerField()),
                ('created', models.DateField(auto_now_add=True)),
                ('delivery_date', models.DateField()),
                ('deliverd', models.BooleanField(default=False)),
                ('clinet', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='base.client')),
                ('products', models.ManyToManyField(related_name='productss', to='base.product')),
            ],
        ),
        migrations.CreateModel(
            name='Incoming_Products',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('num_item', models.IntegerField()),
                ('purch_price', models.FloatField()),
                ('incoming', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='base.incoming')),
                ('products', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='base.product')),
            ],
        ),
        migrations.AddField(
            model_name='incoming',
            name='products',
            field=models.ManyToManyField(through='base.Incoming_Products', to='base.product'),
        ),
        migrations.CreateModel(
            name='Cart_Products',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.IntegerField(default=1)),
                ('cart', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='base.cart')),
                ('products', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='base.product')),
            ],
            options={
                'ordering': ['-products__added'],
            },
        ),
        migrations.AddField(
            model_name='cart',
            name='items',
            field=models.ManyToManyField(through='base.Cart_Products', to='base.product'),
        ),
        migrations.CreateModel(
            name='SalesEmployee',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('representative', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='incoming',
            name='supplier',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='base.supplier'),
        ),
    ]
