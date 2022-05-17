from django.db import models


class DCDepartment(models.Model):
    """ Департамент для сервиса справочника сотрудника / оргструктуры. """
    title = models.CharField(max_length=128)
    create = models.DateTimeField(null=True, blank=True)
    modified = models.DateTimeField(null=True, blank=True)
    department_id = models.CharField(max_length=128)
    firm_id = models.IntegerField()
    struct_code = models.CharField(max_length=128)
    manager_login = models.CharField(max_length=128, null=True, blank=True)
    manager_name = models.CharField(max_length=128, null=True, blank=True)
    users_count = models.IntegerField(default=0)
    struct_level = models.IntegerField()

    parent = models.ForeignKey('self', models.CASCADE, null=True, blank=True, related_name='childs')

    class Meta:
        verbose_name = 'Департамент в орг-структуре'
        verbose_name_plural = 'Департаменты в орг-структуре'

    def __str__(self):
        return self.title

    @property
    def calculata_employees_count(self):
        pass


class DCEmployee(models.Model):
    """ Пользователь из сервиса справочника сотрудника. """
    name = models.CharField(max_length=256)
    login = models.CharField(max_length=64)
    job_title = models.CharField(max_length=256)
    work_email = models.CharField(max_length=128, null=True, blank=True)
    work_phone = models.CharField(max_length=64, null=True, blank=True)
    cell_phone = models.CharField(max_length=64, null=True, blank=True)
    department = models.CharField(max_length=256)
    department_id = models.CharField(max_length=512)
    department_ids = models.CharField(max_length=512)
    path = models.URLField(max_length=512)
    picture_url = models.URLField(max_length=512, null=True, blank=True)
    city = models.CharField(max_length=64)
    organization = models.CharField(max_length=256)
    status = models.CharField(max_length=64)
    work_schedule = models.CharField(max_length=256)
    department_titles = models.CharField(max_length=512, null=True, blank=True)
    ct_id = models.CharField(max_length=256, null=True, blank=True)
    hide = models.IntegerField()
    doc_id = models.IntegerField()
    path_dep = models.CharField(max_length=256, null=True, blank=True)

    departments = models.ManyToManyField(DCDepartment, verbose_name='dc_departments', related_name='dc_users')

    class Meta:
        verbose_name = 'Сотрудник в орг-структуре'
        verbose_name_plural = 'Сотрудник в орг-структуре'

    def __str__(self):
        return self.name
