# Generated by Django 5.0 on 2024-03-08 05:48

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Company_Fund', '0011_alter_debt_client_receipt_num_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='debt_client',
            options={'ordering': ['-id']},
        ),
        migrations.AlterModelOptions(
            name='debt_supplier',
            options={'ordering': ['-id']},
        ),
        migrations.AlterModelOptions(
            name='deposite',
            options={'ordering': ['-id']},
        ),
        migrations.AlterModelOptions(
            name='expense',
            options={'ordering': ['-id']},
        ),
        migrations.AlterModelOptions(
            name='payment',
            options={'ordering': ['-id']},
        ),
        migrations.AlterModelOptions(
            name='recieved_payment',
            options={'ordering': ['-id']},
        ),
        migrations.AlterModelOptions(
            name='withdraw',
            options={'ordering': ['-id']},
        ),
    ]
