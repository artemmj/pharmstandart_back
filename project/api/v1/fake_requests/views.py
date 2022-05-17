from rest_framework import permissions

from apps.helpers.viewsets import ExtendedModelViewSet, paginate_response
from apps.fake_requests.models import FakeRequest
from . import serializers


class FakeRequestViewSet(ExtendedModelViewSet):
    queryset = FakeRequest.objects.all()
    serializer_class = serializers.FakeRequestSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def list(self, request, *args, **kwargs):
        qs = self.get_queryset().filter(user=request.user)
        return paginate_response(self, qs, self.get_serializer)
