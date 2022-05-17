from rest_framework import serializers
from apps.fake_requests.models import FakeRequest


class FakeRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = FakeRequest
        fields = ('id', 'created_at', 'fio', 'email', 'phone', 'message',)
        read_only_fields = ('id', 'created_at',)

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        fakerequest = FakeRequest.objects.create(**validated_data)
        return fakerequest
