import os
import uuid
import logging
import unicodedata
from datetime import datetime

from django.conf import settings
from rest_framework import serializers

from bs4 import BeautifulSoup

from apps.news.models import PersonnelChange
from apps.fs2_api.portal_proxy import PortalApiProxy

logger = logging.getLogger('django')


class PersonnelChangeSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    image_prev = serializers.SerializerMethodField()

    class Meta:
        model = PersonnelChange
        fields = (
            'id', 'announce', 'image', 'image_prev', 'is_top', 'publish_date',
            'text', 'title',
        )

    def get_image(self, obj):
        if obj.image:
            return self.context['request'].build_absolute_uri(obj.image.path).replace('http://', 'https://')

    def get_image_prev(self, obj):
        if obj.image:
            return self.context['request'].build_absolute_uri(obj.image.path).replace('http://', 'https://')


class LoadPersonnelChangesSerializer(serializers.Serializer):
    Announce = serializers.CharField()
    ImagePath = serializers.CharField(allow_null=True)
    ImagePrevPath = serializers.CharField(allow_null=True)
    IsTop = serializers.BooleanField()
    PublishDate = serializers.CharField()
    Text = serializers.CharField()
    Title = serializers.CharField()


class PersonnelChangesLoader:
    def __init__(self):
        self.portal_api = PortalApiProxy(login='aamakarenko', password='dS168xV1^^^')
        PersonnelChange.objects.all().delete()

    def load(self):
        if not os.path.exists(settings.MEDIA_ROOT + '/news'):
            os.mkdir(settings.MEDIA_ROOT + '/news')

        result = self.portal_api.get_news_personnel_changes()['Items']
        for row in result:
            serializer = LoadPersonnelChangesSerializer(data=row)
            if serializer.is_valid():
                announce = serializer.data['Announce']
                image = serializer.data['ImagePath']
                image_prev = serializer.data['ImagePrevPath']
                is_top = serializer.data['IsTop']
                publish_date = datetime.fromtimestamp(int(serializer.data['PublishDate'][6:-10])).strftime('%Y-%m-%d')
                text = serializer.data['Text']
                title = serializer.data['Title']

                PersonnelChange.objects.create(
                    announce=announce,
                    image=self.get_image(f'https://portal.pharmstd.ru{image}') if image else None,
                    image_prev=self.get_image(f'https://portal.pharmstd.ru{image_prev}') if image_prev else None,
                    is_top=is_top,
                    publish_date=publish_date,
                    text=self.clean_html(text),
                    title=title,
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

    def clean_html(self, raw_html):
        soup = BeautifulSoup(raw_html, 'lxml')
        text = unicodedata.normalize('NFKD', soup.text).replace('\u200b', '').replace('  ', '').strip()
        return text
