# Generated by Django 3.0.2 on 2021-02-11 23:46

import apps.news.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('news', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='companyarticle',
            name='image_icon',
            field=models.ImageField(null=True, upload_to=apps.news.models.directory_path),
        ),
        migrations.AddField(
            model_name='pharmmarketarticle',
            name='image_icon',
            field=models.ImageField(null=True, upload_to=apps.news.models.directory_path),
        ),
    ]
