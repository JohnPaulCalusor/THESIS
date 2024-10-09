import django_filters
from .models import User, UserMembership, Event
from django.db.models import Q
from django import forms

class UserFilter(django_filters.FilterSet):
    email = django_filters.CharFilter(lookup_expr='icontains')
    first_name = django_filters.CharFilter(lookup_expr='icontains')
    last_name = django_filters.CharFilter(lookup_expr='icontains')
    id = django_filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name']

class MembershipFilter(django_filters.FilterSet):
    id = django_filters.CharFilter(lookup_expr='icontains')
    membership = django_filters.MultipleChoiceFilter(
        choices = [
            ('1', 'Regular'),
            ('2', 'Special'),
            ('3', 'Affiliate'),
            ('4', 'Lifetime'),
        ]
    )
    membershipVerification = django_filters.BooleanFilter(
        widget=forms.Select(choices=[
            ('', 'All'),
            (True, 'Verified'),
            (False, 'Not Verified')
        ], attrs={'class': 'form-control'})
    )

    class Meta:
        model = UserMembership
        fields = ['id', 'membership', 'membershipVerification']

class EventFilter(django_filters.FilterSet):
    id = django_filters.CharFilter(lookup_expr='icontains')
    eventName = django_filters.CharFilter(lookup_expr='icontains')
    startDate = django_filters.DateFilter(
        field_name='startDate',
        widget=forms.DateInput(
            attrs={
                'type': 'date',
                'class': 'form-control',
                'id' : 'filter-start'
            }
        ),
        label='Start Date'
    )
    endDate = django_filters.DateFilter(
        field_name='endDate',
        widget=forms.DateInput(
            attrs={
                'type': 'date', 
                'class': 'form-control',
                'id' : 'filter-end'
            }
        ),
        label='End Date'
    )

    class Meta:
        model = Event
        fields = ['id', 'eventName', 'startDate', 'endDate']
