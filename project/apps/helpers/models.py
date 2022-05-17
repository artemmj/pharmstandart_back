import uuid

from django.db import models, connection
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone

from .managers import DeletedManager, UserDeletedManager


def get_next_value(name):
    with connection.cursor() as cursor:
        cursor.execute(f"select nextval('{name}');")
        row = cursor.fetchone()
    return row[0]


def get_or_repair_or_create(model, *args, **kwargs):
    obj, _ = model.objects.get_or_create(*args, **kwargs)
    if obj.deleted_at:
        obj.deleted_at = None
        obj.save()
    return obj


def get_or_repair_or_update(model, *args, **kwargs):
    obj, _ = model.objects.update_or_create(*args, **kwargs)
    if obj.deleted_at:
        obj.deleted_at = None
        obj.save()
    return obj


class ForceCleanModel(models.Model):
    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    class Meta:
        abstract = True


class UUIDModel(models.Model):
    id = models.UUIDField(_('ID'), default=uuid.uuid4, primary_key=True, editable=False)

    class Meta:
        abstract = True


class CreatedModel(models.Model):
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)

    class Meta:
        abstract = True


class DeletedModel(models.Model):
    deleted_at = models.DateTimeField(_('deleted at'), db_index=True, null=True, blank=True, editable=False)

    objects = DeletedManager()

    class Meta:
        abstract = True

    def delete(self, using=None, keep_parents=False, force=False):
        if force:
            return super().delete(using=using, keep_parents=keep_parents)
        else:
            self.deleted_at = timezone.now()
            self.save()


class UserDeletedModel(models.Model):
    deleted_at = models.DateTimeField(_('deleted at'), db_index=True, null=True, blank=True, editable=False)

    objects = UserDeletedManager()

    class Meta:
        abstract = True

    def delete(self, using=None, keep_parents=False, force=False):
        if force:
            return super().delete(using=using, keep_parents=keep_parents)
        else:
            self.deleted_at = timezone.now()
            self.save()


class FilterTypes(models.TextChoices):
    GENERAL = 'general', 'общая'
    ACTUAL = 'actual', 'актуальная'
