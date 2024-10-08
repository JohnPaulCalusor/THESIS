import django_filters
from .models import User
from django.db.models import Q

class UserFilter(django_filters.FilterSet):
    email = django_filters.CharFilter(lookup_expr='icontains')
    first_name = django_filters.CharFilter(lookup_expr='icontains')
    last_name = django_filters.CharFilter(lookup_expr='icontains')
    id = django_filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name']
