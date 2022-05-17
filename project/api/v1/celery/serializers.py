from rest_framework import serializers


class BasicCeleryResultSerializer(serializers.Serializer):
    status = serializers.CharField()
    result = serializers.SerializerMethodField()

    def get_result(self, obj):
        try:
            if issubclass(obj.result.__class__, Exception):
                return str(obj.result)
            else:
                return obj.result
        except Exception as e:
            return str(e)
