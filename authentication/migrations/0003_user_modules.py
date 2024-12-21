# Generated by Django 5.1.2 on 2024-12-13 07:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0002_roles_user_roles_fk'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='modules',
            field=models.CharField(choices=[('Reservations', 'Reservations'), ('Logistics', 'Logistics'), ('Finance', 'Finance'), ('None', 'None')], default='None', max_length=50),
        ),
    ]