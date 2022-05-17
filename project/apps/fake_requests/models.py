from django.db import models

from apps.helpers.models import UUIDModel, CreatedModel
from apps.user.models import User


class FakeRequest(UUIDModel, CreatedModel):
    fio = models.CharField('ФИО', max_length=128)
    email = models.EmailField('Имейл')
    phone = models.CharField('Номер телефона', max_length=16, null=True, blank=True)
    message = models.CharField('Сообщение', max_length=512)

    user = models.ForeignKey(User, models.CASCADE, related_name='fake_requests')

    class Meta:
        verbose_name = 'Фейковый запрос'
        verbose_name_plural = 'Фейковые запросы'
