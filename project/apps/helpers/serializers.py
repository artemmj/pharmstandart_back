from drf_extra_fields.fields import DateRangeField
from drf_yasg import openapi
from rest_framework import serializers


class EagerLoadingSerializerMixin:

    select_related_fields = []
    prefetch_related_fields = []

    @classmethod
    def setup_eager_loading(cls, queryset):
        if cls.select_related_fields:
            queryset = queryset.select_related(*cls.select_related_fields)
        if cls.prefetch_related_fields:
            queryset = queryset.prefetch_related(*cls.prefetch_related_fields)
        return queryset


class EmptySerializer(serializers.Serializer):
    pass


class EnumSerializer(serializers.Serializer):
    value = serializers.CharField()
    name = serializers.CharField(source='label')


class DateRangeExtField(DateRangeField):
    class Meta:
        swagger_schema_fields = {
            "type": openapi.TYPE_OBJECT,
            "title": "Period",
            "properties": {
                "lower": openapi.Schema(
                    title="Первый день периода",
                    type=openapi.TYPE_STRING,
                    format=openapi.FORMAT_DATE
                ),
                "upper": openapi.Schema(
                    title="Последний день периода",
                    type=openapi.TYPE_STRING,
                    format=openapi.FORMAT_DATE
                ),
            },
        }


class EnumField(serializers.ChoiceField):
    class Meta:
        pass

    def __init__(self, enum_class, *args, **kwargs):
        EnumField.Meta.swagger_schema_fields = {
            "type": openapi.TYPE_OBJECT,
            "title": "Type",
            "properties": {
                "name": openapi.Schema(
                    title="Email subject",
                    type=openapi.TYPE_STRING,
                    enum=enum_class.labels,
                ),
                "value": openapi.Schema(
                    title="Значение",
                    type=openapi.TYPE_STRING,
                    enum=enum_class.values,
                ),
            },
        }
        self.enum_class = enum_class
        super().__init__(*args, choices=enum_class.choices, **kwargs)

    def to_representation(self, value):
        return EnumSerializer(self.enum_class[value.upper()]).data if value else None


class DeleteBatchRequestSerializer(serializers.Serializer):
    items = serializers.ListField(child=serializers.UUIDField())


class DeleteBatchSerializer(serializers.Serializer):
    def get_fields(self):
        fields = super().get_fields()
        fields['items'] = serializers.PrimaryKeyRelatedField(queryset=self.context['queryset'], many=True)
        return fields


class CompanyAdminsSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    first_name = serializers.CharField()
    last_name = serializers.CharField()
