# Generated by Django 3.0.2 on 2021-01-08 20:54

import apps.homepage.models
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Slider',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=256)),
                ('image', models.ImageField(upload_to=apps.homepage.models.directory_path)),
            ],
        ),
    ]
