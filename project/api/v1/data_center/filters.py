from django_filters import FilterSet, CharFilter

from apps.data_center.models import DCDepartment


class DCEmployeeFilterSet(FilterSet):
    name = CharFilter(field_name='name', lookup_expr='icontains')
    department = CharFilter(field_name='department_ids', lookup_expr='icontains')


class DCDepartmentFilterSet(FilterSet):
    title = CharFilter(field_name='title', lookup_expr='icontains')
    parent = CharFilter(field_name='parent', method='get_childs')

    def get_childs(self, queryset, name, value):
        parent_dep = DCDepartment.objects.get(pk=value)
        return queryset.filter(parent=parent_dep)
