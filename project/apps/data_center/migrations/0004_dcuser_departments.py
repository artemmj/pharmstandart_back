# Generated by Django 3.0.2 on 2021-05-19 07:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('data_center', '0003_auto_20210519_0640'),
    ]

    operations = [
        migrations.AddField(
            model_name='dcuser',
            name='departments',
            field=models.ManyToManyField(related_name='dc_users', to='data_center.DCDepartment', verbose_name='dc_departments'),
        ),
    ]
