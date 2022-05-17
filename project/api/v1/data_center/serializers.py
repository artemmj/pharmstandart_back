from rest_framework import serializers
from drf_yasg.utils import swagger_serializer_method

from apps.data_center.models import DCEmployee, DCDepartment


class EmptySerializer(serializers.Serializer):
    pass


class AddAttachSupReqResultSerializer(serializers.Serializer):
    status = serializers.CharField()


class DCUserSerializer(serializers.ModelSerializer):
    department_titles = serializers.SerializerMethodField()

    class Meta:
        model = DCEmployee
        fields = (
            'id', 'name', 'login', 'job_title', 'work_email', 'work_phone',
            'cell_phone', 'department', 'department_id', 'department_ids',
            'path', 'picture_url', 'city', 'organization', 'status',
            'work_schedule', 'department_titles', 'ct_id', 'hide', 'doc_id',
            'path_dep',
        )

    def get_department_titles(self, obj):
        if obj.department_titles:
            reversed_list = list(reversed(obj.department_titles.split('\n\n')))[1:]
            return ' / '.join(reversed_list)
        return None


class DCListEmployeeResponseSerializer(serializers.Serializer):
    count = serializers.IntegerField()
    result = serializers.ListField(child=DCUserSerializer())


class DCDepartmentSerializer(serializers.ModelSerializer):
    child_depts_count = serializers.SerializerMethodField()

    class Meta:
        model = DCDepartment
        fields = (
            'id', 'title', 'create', 'modified', 'department_id', 'firm_id',
            'struct_code', 'manager_login', 'manager_name', 'users_count',
            'struct_level', 'parent', 'child_depts_count',
        )

    @swagger_serializer_method(serializer_or_field=serializers.IntegerField())
    def get_child_depts_count(self, obj):
        return len(DCDepartment.objects.filter(parent=obj))


class GetDCDeptsQuerySerializer(serializers.Serializer):
    parent = serializers.IntegerField(required=False)


class InitSupportRequestSerializer(serializers.Serializer):
    """ Для ответа от апи фс2 на запрос на инициализацию заявки в ЦОД. """
    defaultsupporttypeid = serializers.CharField()
    defaultpriority = serializers.IntegerField()
    entityid = serializers.CharField()
    name = serializers.CharField()
    caption = serializers.CharField()
    priorities = serializers.ListField()
    SupportTypes = serializers.ListField()
    app_id = serializers.CharField()


class InitSupportRequestMKSerializer(serializers.Serializer):
    """ Для ответа клиенту на запрос на инициализацию заявки в ЦОД. """
    defaultsupporttypeid = serializers.CharField()
    defaultpriority = serializers.IntegerField()
    entityid = serializers.CharField()
    name = serializers.CharField()
    caption = serializers.CharField()
    priorities = serializers.ListField()
    directions = serializers.ListField()
    request_types = serializers.ListField()
    app_id = serializers.CharField()


class SendSupportRequestSerializer(serializers.Serializer):
    """ Непосредственный запрос фс2. """
    entityid = serializers.CharField()
    supporttypeid = serializers.CharField()
    priority = serializers.IntegerField()
    subject = serializers.CharField()
    text = serializers.CharField()
    app_id = serializers.CharField()


class AddAttachToSupportRequestSerializer(serializers.Serializer):
    """ Для отправки на добавление вложения в запросе на заявку ЦОД. """
    file = serializers.FileField()
    entityid = serializers.CharField()
    app_id = serializers.CharField()
