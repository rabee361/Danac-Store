# Generated by Django 5.0 on 2024-02-27 19:37

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Company_Fund', '0002_initial'),
        ('Human_Resources', '0005_remove_extra_expense_barcode'),
    ]

    operations = [
        migrations.AddField(
            model_name='registry',
            name='employee',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='Human_Resources.employee'),
        ),
    ]
