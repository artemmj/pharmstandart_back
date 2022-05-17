from django.db import models


class PharmUser(models.Model):
    pharm_id = models.UUIDField('ID в фармсэде')
    username = models.CharField(max_length=128, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    fio = models.CharField('Инициалы', max_length=128, null=True, blank=True)
    userstate = models.CharField(max_length=256, null=True, blank=True)
    phone1 = models.CharField(max_length=64, null=True, blank=True)
    phone2 = models.CharField(max_length=64, null=True, blank=True)
    firm = models.CharField(max_length=256, null=True, blank=True)
    depart = models.CharField(max_length=256, null=True, blank=True)
    empl = models.CharField(max_length=256, null=True, blank=True)
    abs_reason = models.CharField(max_length=256, null=True, blank=True)

    def __str__(self):
        return f'{self.pharm_id}: {self.fio} / {self.email}'
