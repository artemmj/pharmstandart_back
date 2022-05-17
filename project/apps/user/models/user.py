import base64

from uuid import uuid4

from django.contrib.auth import models as auth_models
from django.db import models
from django_lifecycle import LifecycleModelMixin
from django.contrib.auth.models import UserManager as BaseUserManager
from django.utils import timezone

from phonenumber_field.modelfields import PhoneNumberField

from apps.helpers.models import UUIDModel
from .pharm_session import PharmSession


class UserManager(BaseUserManager):

    def _create_user(self, email, password, is_staff, is_superuser, **extra_fields):
        if not email:
            raise ValueError('Для создания пользователя необходима почта')
        email = self.normalize_email(email)
        user = self.model(
            email=email,
            username=email,
            is_active=True,
            is_staff=is_staff,
            is_superuser=is_superuser,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        return self._create_user(email, password, is_staff=False, is_superuser=False, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        return self._create_user(email, password, is_staff=True, is_superuser=True, **extra_fields)

    def get_by_natural_key(self, username):
        # Для корректной работы JWT и JSONWebTokenSerializer
        return self.get(email=username)


class UserRoles(models.TextChoices):
    admin = 'admin', 'Админ'
    user = 'user', 'Пользователь'


def directory_path(instance, filename):
    return f'avatars/{timezone.now().strftime("%Y/%m/%d")}/{uuid4()}{filename}'


class User(LifecycleModelMixin, UUIDModel, auth_models.AbstractUser):
    email = models.EmailField('Адрес электронной почты', unique=True)
    phone = PhoneNumberField('Номер телефона', help_text='Пример, +79510549236', null=True, blank=True)
    username = models.CharField('Имя пользователя', max_length=100, blank=True)
    # role = models.CharField('Роль', max_length=20, choices=UserRoles.choices)

    first_name = models.CharField('Имя', max_length=30, default='', blank=True)
    middle_name = models.CharField('Отчество', max_length=30, default='', blank=True)
    last_name = models.CharField('Фамилия', max_length=150, default='', blank=True)
    birthday = models.DateField('Дата рожения', null=True, blank=True)
    work_address = models.CharField('Рабочий адрес сотрудника', max_length=256, null=True, blank=True)
    about = models.CharField('Обо мне', max_length=512, null=True, blank=True)
    skills = models.CharField('Навыки и умения', max_length=1024, null=True, blank=True)

    encryptedpass = models.CharField(max_length=256, default='')
    image = models.ImageField('Аватар', blank=True, null=True, upload_to=directory_path)

    pharm_session = models.ForeignKey(PharmSession, on_delete=models.CASCADE, null=True, blank=True)
    is_test_user = models.BooleanField('Тестовый пользователь', default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['phone']

    objects = UserManager()

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def get_username(self):
        # for jwt_payload_handler
        return str(self.email)

    def __str__(self):
        return self.email

    @property
    def get_enc_pass(self):
        return base64.b64decode(self.encryptedpass.encode('UTF-8')).decode('UTF-8')
