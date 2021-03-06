# Generated by Django 3.0.2 on 2021-05-17 04:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('data_center', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='DCDepartment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=128)),
                ('create', models.CharField(max_length=128)),
                ('modified', models.CharField(max_length=128)),
                ('department_id', models.CharField(max_length=128)),
                ('parent_id', models.CharField(blank=True, max_length=128, null=True)),
                ('firm_id', models.IntegerField()),
                ('struct_code', models.CharField(max_length=128)),
                ('manager_login', models.CharField(blank=True, max_length=128, null=True)),
                ('manager_name', models.CharField(blank=True, max_length=128, null=True)),
                ('users_count', models.IntegerField()),
                ('struct_level', models.IntegerField()),
            ],
        ),
        migrations.AlterField(
            model_name='dcuser',
            name='cell_phone',
            field=models.CharField(blank=True, max_length=64, null=True),
        ),
        migrations.AlterField(
            model_name='dcuser',
            name='ct_id',
            field=models.CharField(blank=True, max_length=256, null=True),
        ),
        migrations.AlterField(
            model_name='dcuser',
            name='department',
            field=models.CharField(max_length=256),
        ),
        migrations.AlterField(
            model_name='dcuser',
            name='department_id',
            field=models.CharField(max_length=512),
        ),
        migrations.AlterField(
            model_name='dcuser',
            name='department_ids',
            field=models.CharField(max_length=512),
        ),
        migrations.AlterField(
            model_name='dcuser',
            name='department_titles',
            field=models.CharField(blank=True, max_length=512, null=True),
        ),
        migrations.AlterField(
            model_name='dcuser',
            name='job_title',
            field=models.CharField(max_length=256),
        ),
        migrations.AlterField(
            model_name='dcuser',
            name='name',
            field=models.CharField(max_length=256),
        ),
        migrations.AlterField(
            model_name='dcuser',
            name='organization',
            field=models.CharField(max_length=256),
        ),
        migrations.AlterField(
            model_name='dcuser',
            name='path',
            field=models.URLField(max_length=512),
        ),
        migrations.AlterField(
            model_name='dcuser',
            name='path_dep',
            field=models.CharField(blank=True, max_length=256, null=True),
        ),
        migrations.AlterField(
            model_name='dcuser',
            name='picture_url',
            field=models.URLField(blank=True, max_length=512, null=True),
        ),
        migrations.AlterField(
            model_name='dcuser',
            name='status',
            field=models.CharField(max_length=64),
        ),
        migrations.AlterField(
            model_name='dcuser',
            name='work_phone',
            field=models.CharField(blank=True, max_length=64, null=True),
        ),
        migrations.AlterField(
            model_name='dcuser',
            name='work_schedule',
            field=models.CharField(max_length=256),
        ),
    ]
