# Generated by Django 3.0.2 on 2021-05-19 08:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('data_center', '0006_auto_20210519_0805'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dcdepartment',
            name='firm_id',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
