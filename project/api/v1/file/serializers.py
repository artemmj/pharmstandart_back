from rest_framework import serializers

from apps.file.models import File


class FileSerializer(serializers.ModelSerializer):
    file = serializers.FileField(required=True)

    class Meta:
        model = File
        fields = (
            'id',
            'file',
        )

        read_only_fields = ('id',)
