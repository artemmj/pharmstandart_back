# Generated by Django 3.0.2 on 2020-12-16 21:54

import apps.user.models
from django.db import migrations, models
import django.utils.timezone
import django_lifecycle.mixins
import phonenumber_field.modelfields
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0011_update_proxy_permissions'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(max_length=254, unique=True, verbose_name='Адрес электронной почты')),
                ('phone', phonenumber_field.modelfields.PhoneNumberField(help_text='Пример, +79510549236', max_length=128, region=None, unique=True, verbose_name='Номер телефона')),
                ('username', models.CharField(blank=True, max_length=100, unique=True, verbose_name='Имя пользователя')),
                ('first_name', models.CharField(blank=True, default='', max_length=30, verbose_name='Имя')),
                ('middle_name', models.CharField(blank=True, default='', max_length=30, verbose_name='Отчество')),
                ('last_name', models.CharField(blank=True, default='', max_length=150, verbose_name='Фамилия')),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'Пользователь',
                'verbose_name_plural': 'Пользователи',
            },
            bases=(django_lifecycle.mixins.LifecycleModelMixin, models.Model),
            managers=[
                ('objects', apps.user.models.UserManager()),
            ],
        ),
    ]
