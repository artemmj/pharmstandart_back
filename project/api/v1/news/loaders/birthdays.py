import os
import uuid
import logging
from datetime import datetime

from django.conf import settings
from rest_framework import serializers

from apps.news.models import Birthday
from apps.fs2_api.portal_proxy import PortalApiProxy

logger = logging.getLogger('django')


class BirthdaySerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = Birthday
        fields = ('id', 'date', 'image', 'job_title', 'name',)

    def get_image(self, obj):
        return self.context['request'].build_absolute_uri(obj.image.path).replace('http://', 'https://')


class LoadBirthdaysSerializer(serializers.Serializer):
    Date = serializers.CharField()
    ImagePath = serializers.CharField()
    JobTitle = serializers.CharField()
    Name = serializers.CharField()


class BirthdaysLoader:
    def __init__(self):
        self.portal_api = PortalApiProxy(login='aamakarenko', password='dS168xV1^^^')
        Birthday.objects.all().delete()

    def load(self):
        if not os.path.exists(settings.MEDIA_ROOT + '/news'):
            os.mkdir(settings.MEDIA_ROOT + '/news')

        result = self.portal_api.get_news_birthdays()['Items']
        for row in result:
            serializer = LoadBirthdaysSerializer(data=row)
            if serializer.is_valid():
                job_title = serializer.data['JobTitle']
                name = serializer.data['Name']
                birth_date = datetime.fromtimestamp(int(serializer.data['Date'][6:-10])).strftime('%Y-%m-%d')
                image = self.get_image(serializer.data['ImagePath'])
                Birthday.objects.create(
                    date=birth_date,
                    image=image,
                    job_title=job_title,
                    name=name
                )
            else:
                logger.info(f'Ошибка при сериализации! ({serializer.errors})')

    def get_image(self, url):
        response = self.portal_api.request('get', url, stream=True)
        ext = url.split('/')[-1].split('.')[-1]
        file_dest = settings.MEDIA_ROOT + '/news/' + f'{uuid.uuid4()}.{ext}'
        with open(file_dest, 'wb') as fd:
            for chunk in response.iter_content(128):
                fd.write(chunk)
        return file_dest
