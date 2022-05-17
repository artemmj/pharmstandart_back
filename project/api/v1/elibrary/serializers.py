from rest_framework import serializers


class ELibExternStatusSerializer(serializers.Serializer):
    """ Обрабатывает ответ от апи портала по статусам elib. """

    class _ItemsSerializer(serializers.Serializer):
        Name = serializers.CharField()

    s_error = serializers.BooleanField()
    s_message = serializers.CharField(allow_null=True)
    s_time = serializers.DateTimeField()
    Items = serializers.ListField(child=_ItemsSerializer())


class ELibInternStatusSerializer(serializers.Serializer):
    """ Для отдачи мобилкам и для свагера инфы по статусам elib. """
    Name = serializers.CharField()


class ELibExternRubricSerializer(serializers.Serializer):
    """ Обрабатывает ответ от апи портала по рубрикам elib. """

    class _ItemsSerializer(serializers.Serializer):
        Name = serializers.CharField()

    s_error = serializers.BooleanField()
    s_message = serializers.CharField(allow_null=True)
    s_time = serializers.DateTimeField()
    Items = serializers.ListField(child=_ItemsSerializer())


class ELibInternRubricSerializer(serializers.Serializer):
    """ Для отдачи мобилкам и для свагера инфы по рубрикам elib. """
    Name = serializers.CharField()


class ELibExternCategorySerializer(serializers.Serializer):
    """ Обрабатывает ответ от апи портала по категориям elib. """
    class _ItemsSerializer(serializers.Serializer):
        Name = serializers.CharField()

    s_error = serializers.BooleanField()
    s_message = serializers.CharField(allow_null=True)
    s_time = serializers.DateTimeField()
    Items = serializers.ListField(child=_ItemsSerializer())


class ELibInternCategorySerializer(serializers.Serializer):
    """ Для отдачи мобилкам и для свагера инфы по категориям elib. """
    Name = serializers.CharField()


class ELibSearchRequestSerializer(serializers.Serializer):
    """ Сериализатор запроса мк на поиск в elib. """
    Category = serializers.ListField(child=serializers.CharField(), required=False)
    Rubric = serializers.ListField(child=serializers.CharField(), required=False)
    Status = serializers.ListField(child=serializers.CharField(), required=False)
    Department = serializers.CharField(required=False)
    Text = serializers.CharField(required=False)
    Date = serializers.ListField(child=serializers.DateTimeField(), required=False)


class ELibSearchResponseSerializer(serializers.Serializer):
    ''' Сериализатор ответа на запрос поиска. '''
    Title = serializers.CharField(allow_null=True)
    Path = serializers.CharField(allow_null=True)
    Category = serializers.CharField()
    Document = serializers.CharField()
    # DocumentPath = serializers.CharField()
    Author = serializers.CharField(allow_null=True)
    AuthorPath = serializers.URLField(allow_null=True)
    Status = serializers.CharField()
    Date = serializers.DateTimeField()
    LinkedDocs = serializers.CharField(allow_null=True)


class ELibSearchResponseWithDocPathSerializer(ELibSearchResponseSerializer):
    ''' Сериализатор ответа на запрос поиска (включает в себя DocumentPath).
    '''
    DocumentPath = serializers.CharField()


class ELibListQuerySerializer(serializers.Serializer):
    ''' Сериализатор на квери параметры list запроса elib. '''
    status = serializers.CharField(required=False)


class ELibRetrieveSerializer(ELibSearchResponseSerializer):
    ''' Сериализатор на ответ на детальный вид в электронной библиотеке. '''
    DocumentPath = serializers.CharField()
