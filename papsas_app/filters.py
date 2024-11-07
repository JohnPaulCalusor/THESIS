import django_filters
from .models import Candidacy, User, UserMembership, Election, Event, EventRegistration, Attendance, Venue, Achievement, NewsandOffers, Candidacy, EventRating
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
            ('4', 'Affiliate'),
            ('5', 'Lifetime'),
        ]
    )
    status = django_filters.ChoiceFilter(
        choices=[
            ('Approved', 'Approved'),
            ('Pending', 'Pending'),
            ('Declined', 'Declined'),
        ], 
        empty_label='All',
        initial=''
        )

    class Meta:
        model = UserMembership
        fields = ['id', 'membership', 'status']

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

class EventRegistrationFilter(django_filters.FilterSet):
    id = django_filters.CharFilter(lookup_expr='icontains')
    user = django_filters.CharFilter(method='user_filter')
    status = django_filters.CharFilter(
        widget=forms.Select(choices=[
            ('', 'All'),
            ('Approved', 'Approved'),
            ('Pending', 'Pending'),
            ('Declined', 'Declined')
        ], attrs={'class': 'form-control'})        
    )
    class Meta:
        model = EventRegistration
        fields = ['id', 'user', 'status']
        
    def user_filter(self, queryset, name, value):
        return queryset.filter(user__first_name__icontains=value) | queryset.filter(user__last_name__icontains=value)

class AttendanceFilter(django_filters.FilterSet):
    id = django_filters.CharFilter(lookup_expr='icontains')
    user = django_filters.CharFilter(method='user_filter')
    attended = django_filters.CharFilter(
        widget=forms.Select(choices=[
            ('', 'All'),
            ('True', 'Attended'),
            ('False', 'Absent'),
            ], attrs={'class': 'form-control'})
            )
    class Meta:
        model = Attendance
        fields = ['id', 'user', 'attended']

    def user_filter(self, queryset, name, value):
        return queryset.filter(user__first_name__icontains=value) | queryset.filter(user__last_name__icontains=value)
    
class VenueFilter(django_filters.FilterSet):
    id = django_filters.CharFilter(lookup_expr='icontains')
    name = django_filters.CharFilter(lookup_expr='icontains',
                                     widget=forms.TextInput(attrs={'id': 'name-id'}))
    address = django_filters.CharFilter(lookup_expr='icontains',
                                        widget=forms.TextInput(attrs={'id': 'address-id'}))

    class Meta:
        model = Venue
        fields = ['id', 'name', 'address']

class AchievementFilter(django_filters.FilterSet):
    id = django_filters.CharFilter(lookup_expr='icontains')
    name = django_filters.CharFilter(lookup_expr='icontains',
                                     widget=forms.TextInput(attrs={'id': 'name-id'}))

    class Meta:
        model = Achievement
        fields = ['id', 'name']

class NewsAndOfferFilter(django_filters.FilterSet):
    id = django_filters.CharFilter(lookup_expr='icontains')
    name = django_filters.CharFilter(lookup_expr='icontains',
                                     widget=forms.TextInput(attrs={'id': 'name-id'}))

    class Meta:
        model = NewsandOffers
        fields = ['id', 'name']

class ElectionFilter(django_filters.FilterSet):
    title = django_filters.CharFilter(lookup_expr='icontains',
                                     widget=forms.TextInput(attrs={'id': 'title-id'}))
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
        model = Election
        fields = ['id', 'title', 'startDate', 'endDate']

class CandidateFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains',
                                     widget=forms.TextInput(attrs={'id': 'name-id'}))

    class Meta:
        model = Candidacy
        fields = ['id']

    def filter_name(self, queryset, name, value):
        return queryset.filter(candidate__first_name__icontains=value) | queryset.filter(candidate__last_name__icontains=value)

class FeedbackFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains')
    
    class Meta:
        model = EventRating
        fields = ['id', 'user', 'rating']