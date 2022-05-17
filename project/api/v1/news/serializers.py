from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from apps.news.models import Tag, PharmMarketArticle, CompanyArticle


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name',)


class ArticleTagsSerializer(serializers.RelatedField):
    def to_representation(self, value):
        return value.name

    class Meta:
        model = Tag


class CompanySerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(source='publish_date')
    tags = ArticleTagsSerializer(label=_('tags'), many=True, read_only=True)
    image = serializers.SerializerMethodField()

    class Meta:
        model = CompanyArticle
        fields = ('id', 'title', 'description', 'image', 'created_at', 'tags',)

    def get_image(self, obj):
        return self.context['request'].build_absolute_uri(obj.image.path).replace('http://', 'https://')


class PharmMarketSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(source='publish_date')
    tags = ArticleTagsSerializer(label=_('tags'), many=True, read_only=True)
    image = serializers.SerializerMethodField()

    class Meta:
        model = PharmMarketArticle
        fields = ('id', 'title', 'description', 'image', 'created_at', 'tags',)

    def get_image(self, obj):
        return self.context['request'].build_absolute_uri(obj.image.path).replace('http://', 'https://')
