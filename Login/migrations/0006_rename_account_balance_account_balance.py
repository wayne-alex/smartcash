# Generated by Django 4.2.3 on 2024-07-07 19:56

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Login', '0005_payment'),
    ]

    operations = [
        migrations.RenameField(
            model_name='account',
            old_name='account_balance',
            new_name='balance',
        ),
    ]
