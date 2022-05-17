import logging
import re
import unicodedata
import uuid

from django.conf import settings
from django.db import transaction

from rest_framework import serializers
from bs4 import BeautifulSoup

from apps.news.models import Tag, CompanyArticle, PharmMarketArticle
from apps.fs2_api.portal_proxy import PortalApiProxy

logger = logging.getLogger('django')


class PortalNewsSerializer(serializers.Serializer):
    Id = serializers.IntegerField()
    Title = serializers.CharField()
    PublishDate = serializers.DateTimeField()
    IsMainNewsItem = serializers.BooleanField()
    Body = serializers.CharField()
    TaxKeyword = serializers.JSONField()
    NewsImage = serializers.CharField()
    NewsImageIcon = serializers.CharField(allow_null=True)


class NewsLoader:
    '''
    Родительский класс для загрузки/актуализации новостей в БД.
    '''
    api_url = 'https://portal.pharmstd.ru'
    api_news_url = 'https://portal.pharmstd.ru/_vti_bin/MobileStd/News.svc'
    api_url_suffix = None  # тип новостей - фармрынка или компании (Press / Gk)
    model = None  # модель, используемая для актуализации (CompanyArticle / PharmMarketArticle)

    def __init__(self):
        self.fs2_api = PortalApiProxy(login='aamakarenko', password='dS168xV1^^^')

    def load(self):
        response, _ = self.fs2_api.json_request('get', f'{self.api_news_url}/{self.api_url_suffix}All')
        result = response.get('Result', [])
        for item in result:
            self.save_news_entity(item['Id'])

    @transaction.atomic
    def save_news_entity(self, entity_id):
        response, _ = self.fs2_api.json_request('get', f'{self.api_news_url}/{self.api_url_suffix}ById?id={entity_id}')
        serializer = PortalNewsSerializer(data=response['Result'][0])

        if serializer.is_valid():
            validated_data = serializer.validated_data

            match_image = re.findall(r'src="([^"]+)"', validated_data['NewsImage'])
            image = self.get_image(f'{self.api_url}/{match_image[0]}')

            image_icon = None
            if validated_data['NewsImageIcon']:
                match_image_icon = re.findall(r'src="([^"]+)"', validated_data['NewsImageIcon'])
                image_icon = self.get_image(f'{self.api_url}/{match_image_icon[0]}')

            article, _ = self.model.objects.get_or_create(
                portal_id=validated_data['Id'],
                defaults={
                    'entity': response['Result'],
                    'publish_date': validated_data['PublishDate'],
                    'is_main': validated_data['IsMainNewsItem'],
                    'title': self.clean_html(validated_data['Title']),
                    'description': self.clean_html(validated_data['Body']),
                    'image': image,
                    'image_icon': image_icon,
                },
            )

            article.tags.all().delete()
            tags = [
                Tag.objects.update_or_create(portal_id=k, defaults={'name': v})[0]
                for k, v in validated_data['TaxKeyword'].items()
            ]
            article.tags.add(*tags)
        else:
            logger.error(str(serializer.errors))

    def get_image(self, url):
        response = self.fs2_api.request('get', url, stream=True)

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


class CompanyNewsLoader(NewsLoader):
    api_url_suffix = 'Gk'
    model = CompanyArticle


class PharmMarketNewsLoader(NewsLoader):
    api_url_suffix = 'Press'
    model = PharmMarketArticle
