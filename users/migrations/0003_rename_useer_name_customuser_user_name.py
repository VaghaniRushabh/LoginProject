# Generated by Django 4.2.4 on 2023-08-22 04:19

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_otp'),
    ]

    operations = [
        migrations.RenameField(
            model_name='customuser',
            old_name='useer_name',
            new_name='user_name',
        ),
    ]
