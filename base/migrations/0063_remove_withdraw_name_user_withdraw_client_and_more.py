# Generated by Django 4.2.8 on 2023-12-26 09:01

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0062_advance_on_salary_extra_expense_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='withdraw',
            name='name_user',
        ),
        migrations.AddField(
            model_name='withdraw',
            name='client',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='base.client'),
        ),
        migrations.AlterField(
            model_name='codeverivecation',
            name='expires_at',
            field=models.DateTimeField(default=datetime.datetime(2023, 12, 26, 9, 11, 14, 753092, tzinfo=datetime.timezone.utc)),
        ),
    ]
