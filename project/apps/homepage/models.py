from uuid import uuid4

from django.db import models
from django.utils import timezone


def directory_path(instance, filename):
    return f'sliders/{timezone.now().strftime("%Y/%m/%d")}/{uuid4()}{filename}'


class Slider(models.Model):
    title = models.CharField(max_length=256)
    image = models.ImageField(upload_to=directory_path)  # FileField
