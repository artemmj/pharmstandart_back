# Generated by Django 3.0.2 on 2021-06-29 08:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('news', '0002_auto_20210211_2346'),
    ]

    operations = [
        migrations.AlterField(
            model_name='companyarticle',
            name='image',
            field=models.ImageField(null=True, upload_to=''),
        ),
        migrations.AlterField(
            model_name='companyarticle',
            name='image_icon',
            field=models.ImageField(null=True, upload_to=''),
        ),
        migrations.AlterField(
            model_name='pharmmarketarticle',
            name='image',
            field=models.ImageField(null=True, upload_to=''),
        ),
        migrations.AlterField(
            model_name='pharmmarketarticle',
            name='image_icon',
            field=models.ImageField(null=True, upload_to=''),
        ),
    ]
