# Generated by Django 5.0 on 2024-03-08 09:14

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Human_Resources', '0006_alter_absence_date_alter_advance_on_salary_date_and_more'),
        ('base', '0031_remove_returnedclientpackage_client_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='damagedproduct',
            name='employee',
        ),
        migrations.AddField(
            model_name='damagedpackage',
            name='employee',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='Human_Resources.employee'),
        ),
    ]
