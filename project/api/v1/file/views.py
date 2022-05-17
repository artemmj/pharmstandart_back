from rest_framework.parsers import MultiPartParser

from apps.file.models import File
from apps.helpers.batchmixin import DeleteBatchMixin
from apps.helpers.viewsets import ExtendedModelViewSet

from .serializers import FileSerializer


class FileViewSet(ExtendedModelViewSet, DeleteBatchMixin):
    queryset = File.objects.all().non_deleted()
    serializer_class = FileSerializer
    parser_classes = (MultiPartParser,)
