from rest_framework import serializers

from apps.homepage.models import Slider


class HomepageGetTasksCountSerializer(serializers.Serializer):
    """ Сериализатор счетчика задач на главной странице """
    Count = serializers.IntegerField()
    s_error = serializers.BooleanField()
    s_message = serializers.CharField()
    s_time = serializers.DateTimeField()


class HomepageGetMailsCountSerializer(serializers.Serializer):
    """ Сериализатор счетчика писем на главной странице """
    Count = serializers.IntegerField()
    s_error = serializers.BooleanField()
    s_message = serializers.CharField()
    s_time = serializers.DateTimeField()


class HomepageDocumentsDefaultActionsSerializer(serializers.Serializer):
    """ Действия по-умолчанию в документах на домашней странице """
    id = serializers.IntegerField()
    caption = serializers.CharField()
    status = serializers.CharField()


class HomepageFullDocumentsSerializer(serializers.Serializer):
    """ Сериализатор документов домашней страницы, разбито по статусам """

    class HomepageDocumentsSerializer(serializers.Serializer):
        """ Документы в каждом из возможных статусов """
        requires_attention = serializers.CharField()
        name = serializers.CharField()
        amount = serializers.FloatField()
        date_deadline = serializers.DateField()
        source = serializers.CharField()
        default_actions = serializers.ListField(child=HomepageDocumentsDefaultActionsSerializer())

    status_name = serializers.CharField()
    status_count = serializers.IntegerField()
    documents = serializers.ListSerializer(child=HomepageDocumentsSerializer())


class HomepageSlidersSerializer(serializers.ModelSerializer):
    class Meta:
        model = Slider
        fields = ('id', 'title', 'image',)


class HomepageTollsSerializer(serializers.Serializer):
    """ Сериализатор для ссылок на домашней странице """
    taxi = serializers.CharField()
    delivery_service = serializers.CharField()
    booking = serializers.CharField()
