# Generated by Django 5.0 on 2024-01-10 13:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Clients_and_Products', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='client',
            name='category',
            field=models.CharField(choices=[('سوبرماركت', 'سوبرماركت'), ('مقهى', 'مقهى'), (' جملة', ' جملة'), (' نصف جملة', ' نصف جملة'), ('مطعم', 'مطعم'), ('تجزئة', 'تجزئة')], max_length=75),
        ),
    ]
