from django_filters import (
    FilterSet, ModelMultipleChoiceFilter, DateFromToRangeFilter,
)

from apps.news.models import CompanyArticle, PharmMarketArticle, Tag


class CompanyArticleFilterSet(FilterSet):
    tag = ModelMultipleChoiceFilter(
        field_name="tags__name",
        to_field_name='name',
        queryset=Tag.objects.all(),
    )
    created_at = DateFromToRangeFilter('publish_date')

    class Meta:
        model = CompanyArticle
        fields = ('id', 'tags',)


class PharmMarketArticleFilterSet(FilterSet):
    tag = ModelMultipleChoiceFilter(
        field_name="tags__name",
        to_field_name='name',
        queryset=Tag.objects.all(),
    )
    created_at = DateFromToRangeFilter('publish_date')

    class Meta:
        model = PharmMarketArticle
        fields = ('id', 'tags',)
