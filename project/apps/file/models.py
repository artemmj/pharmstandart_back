from uuid import uuid4

from django.db import models
from django.utils import timezone

from apps.helpers.models import UUIDModel, CreatedModel, DeletedModel


def directory_path(instance, filename):
    return f'upload/{timezone.now().strftime("%Y/%m/%d")}/{uuid4()}{filename}'


class File(UUIDModel, CreatedModel, DeletedModel):
    file = models.FileField(upload_to=directory_path)

    class Meta:
        verbose_name = 'Файл'
        verbose_name_plural = 'Файлы'

    def __str__(self):
        return self.file.url
