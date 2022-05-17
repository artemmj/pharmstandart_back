
from django.contrib.auth import get_user_model
from django.db.models import Q

from django_filters import FilterSet, CharFilter


User = get_user_model()


class UserFilterSet(FilterSet):
    search_login = CharFilter(method='filter_search_login')

    class Meta:
        model = User
        fields = ('first_name', 'middle_name', 'last_name', 'email', 'phone')

    def filter_search_login(self, queryset, name, value):
        return queryset.filter(Q(phone=value) or Q(email=value))
