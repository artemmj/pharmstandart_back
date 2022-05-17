# Generated by Django 3.0.2 on 2021-05-19 07:47

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('data_center', '0004_dcuser_departments'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='DCUser',
            new_name='DCEmployee',
        ),
        migrations.AlterModelOptions(
            name='dcdepartment',
            options={'verbose_name': 'Департамент в орг-структуре', 'verbose_name_plural': 'Департаменты в орг-структуре'},
        ),
        migrations.AlterModelOptions(
            name='dcemployee',
            options={'verbose_name': 'Сотрудник в орг-структуре', 'verbose_name_plural': 'Сотрудник в орг-структуре'},
        ),
    ]
