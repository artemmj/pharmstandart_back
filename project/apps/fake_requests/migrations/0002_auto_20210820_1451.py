# Generated by Django 3.0.2 on 2021-08-20 14:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fake_requests', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='fakerequest',
            name='phone',
            field=models.CharField(max_length=16, verbose_name='Номер телефона'),
        ),
    ]
