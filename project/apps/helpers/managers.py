from django.contrib.auth.models import UserManager as BaseUserManager
from django.db import models
from django.utils import timezone


# TODO need refactor, extra query
class DeletedQueryMixin(models.query.QuerySet):
    def delete(self, force=False):
        if force:
            return super().delete()
        else:
            return self._delete()

    def _delete(self):
        return (
            self.count(),
            self.update(deleted_at=timezone.now())
        )

    def deleted(self):
        return self.filter(deleted_at__isnull=False)

    def non_deleted(self):
        return super().filter(deleted_at__isnull=True)


class DeletedQuerySet(DeletedQueryMixin, models.query.QuerySet):
    pass


class DeletedManager(models.Manager):
    def get_queryset(self):
        return DeletedQuerySet(self.model, using=self._db)

    def deleted(self):
        return self.get_queryset().filter(deleted_at__isnull=False)

    def non_deleted(self):
        return self.get_queryset().filter(deleted_at__isnull=True)


class UserDeletedManager(DeletedManager, BaseUserManager):
    def create_user(self, phone, password=None, **other_fields):
        """
        Creates and saves a User with the given phone and password.
        """
        if not phone:
            raise ValueError('Users must have an phone')

        user = self.model(phone=phone, **other_fields)

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone, password=None, **other_fields):
        """
        Creates and saves a superuser with the given phone and password.
        """
        user = self.create_user(phone=phone, password=password,**other_fields)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user
