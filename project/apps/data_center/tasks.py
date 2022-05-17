import uuid
import pytz
import logging
from datetime import datetime

from django.db import transaction
from rest_framework import serializers

from apps import app
from apps.fs2_api.portal_proxy import PortalApiProxy
from .models import DCEmployee, DCDepartment

logger = logging.getLogger('django')


class DCUserSerializer(serializers.Serializer):
    Name = serializers.CharField()
    Login = serializers.CharField()
    JobTitle = serializers.CharField()
    WorkEmail = serializers.CharField(allow_null=True)
    WorkPhone = serializers.CharField(allow_null=True)
    CellPhone = serializers.CharField(allow_null=True, allow_blank=True)
    Department = serializers.CharField()
    DepartmentId = serializers.CharField()
    DepartmentIds = serializers.CharField()
    Path = serializers.CharField()
    PictureURL = serializers.CharField(allow_null=True)
    City = serializers.CharField()
    Organization = serializers.CharField()
    Status = serializers.CharField()
    WorkShedule = serializers.CharField()
    DepartmentTitles = serializers.CharField(allow_null=True)
    CtId = serializers.CharField(allow_null=True)
    Hide = serializers.IntegerField()
    DocId = serializers.IntegerField()
    PathDep = serializers.CharField(allow_null=True)


class DCDepartStructureSerializer(serializers.Serializer):
    Id = serializers.IntegerField()
    Title = serializers.CharField()
    Create = serializers.CharField()
    Modified = serializers.CharField()
    DepartmentId = serializers.CharField()
    ParentId = serializers.CharField(allow_null=True, allow_blank=True)
    FirmId = serializers.IntegerField()
    StructCode = serializers.CharField()
    ManagerLogin = serializers.CharField(allow_null=True, allow_blank=True)
    ManagerName = serializers.CharField(allow_null=True, allow_blank=True)
    UsersCount = serializers.IntegerField()
    StructLevel = serializers.IntegerField()


@app.task
@transaction.atomic()
def actualize_org_structure():
    DCEmployee.objects.all().delete()
    DCDepartment.objects.all().delete()
    logger.info('Старые данные успешно удалены...')

    # Орг структура департаментов
    api = PortalApiProxy('aamakarenko', 'dS168xV1^^^')
    result = api.get_structure_from_empcatalog()
    rows = result.get('Rows', list)
    for row in rows:
        serializer = DCDepartStructureSerializer(data=row)
        serializer.is_valid(raise_exception=True)
        data = serializer.data.copy()

        data['Create'] = datetime.fromtimestamp(int(data['Create'][6:16]), tz=pytz.UTC)
        data['Modified'] = datetime.fromtimestamp(int(data['Modified'][6:16]), tz=pytz.UTC)
        data['DepartmentId'] = uuid.UUID(data['DepartmentId'])

        DCDepartment.objects.create(
            id=data['Id'],
            title=data['Title'],
            create=data['Create'],
            modified=data['Modified'],
            department_id=data['DepartmentId'],
            firm_id=data['FirmId'],
            struct_code=data['StructCode'],
            manager_login=data['ManagerLogin'],
            manager_name=data['ManagerName'],
            # users_count=data['UsersCount'],
            struct_level=data['StructLevel'],
        )
    # Проставить родителей
    for row in rows:
        serializer = DCDepartStructureSerializer(row)
        data = serializer.data.copy()

        parent_id = data['ParentId']
        if parent_id:
            dept = DCDepartment.objects.get(pk=data['Id'])
            try:
                parent_dept = DCDepartment.objects.get(pk=parent_id)
                dept.parent = parent_dept
                dept.save()
            except Exception:
                continue
    logger.info('Загружены департаменты')

    # Сотрудники
    result = api.get_employees_from_empcatalog()
    rows = result.get('Rows', list)
    for row in rows:
        serializer = DCUserSerializer(data=row)
        serializer.is_valid(raise_exception=True)

        new_user = DCEmployee.objects.create(
            name=serializer.data['Name'],
            login=serializer.data['Login'],
            job_title=serializer.data['JobTitle'],
            work_email=serializer.data['WorkEmail'],
            work_phone=serializer.data['WorkPhone'],
            cell_phone=serializer.data['CellPhone'],
            department=serializer.data['Department'],
            department_id=serializer.data['DepartmentId'],
            department_ids=serializer.data['DepartmentIds'],
            path=serializer.data['Path'],
            picture_url=serializer.data['PictureURL'],
            city=serializer.data['City'],
            organization=serializer.data['Organization'],
            status=serializer.data['Status'],
            work_schedule=serializer.data['WorkShedule'],
            department_titles=serializer.data['DepartmentTitles'],
            ct_id=serializer.data['CtId'],
            hide=serializer.data['Hide'],
            doc_id=serializer.data['DocId'],
            path_dep=serializer.data['PathDep'],
        )
        depart_ids = serializer.data['DepartmentIds'].split(';')
        for depart_id in depart_ids:
            try:
                department = DCDepartment.objects.get(department_id=depart_id)
                new_user.departments.add(department)
                department.users_count += 1
                department.save()
            except DCDepartment.DoesNotExist:
                continue
    logger.info('Загружены пользователи')
