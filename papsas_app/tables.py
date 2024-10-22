import django_tables2 as tables
from django.utils.html import format_html
from .models import User, UserMembership, Event, EventRegistration, Attendance, Venue, Achievement, NewsandOffers, Election, Vote, Candidacy
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.db.models import Count

class UserTable(tables.Table):
    actions = tables.TemplateColumn(template_name='papsas_app/partial_list/user_action_column.html', orderable=False, verbose_name='Actions')
    profilePic = tables.Column(orderable=False, verbose_name="Profile Picture")

    def render_profilePic(self, record):
            return format_html('<img src="{}" width="40px" height="40px">', record.profilePic.url)
    
    class Meta:
        model = User
        template_name = "django_tables2/bootstrap.html"
        fields = ("id", "first_name", "last_name", "email", "address", "region", "occupation", "age", "is_active" , "birthdate", "email_verified", "profilePic", "institution"    )

class MembershipTable(tables.Table):
    status = tables.Column(orderable=True, verbose_name="Status", attrs={"td": {"class": "status-column"}})
    actions = tables.TemplateColumn(template_name='papsas_app/partial_list/membership_action_column.html', orderable=False, verbose_name='Actions')
    first_name = tables.Column(accessor='user.first_name', verbose_name='First Name')
    last_name = tables.Column(accessor='user.last_name', verbose_name='Last Name')
    registrationDate = tables.Column(orderable=True, verbose_name="Registration Date")
    expirationDate = tables.Column(orderable=True, verbose_name="Expiration Date")
    verificationID = tables.Column(orderable=True, verbose_name="Verification Id")

    def render_verificationID(self, value):
        if value:
            return format_html('<a href="{}" target=""><img src="{}" width="50" height="50"></a>', 
                            value.url, value.url)
        return ''
    
    def render_receipt(self, record):
        return format_html('<img src="{}" width="50" height="50">', record.receipt.url)
    
    class Meta:
        model = UserMembership
        template_name = "django_tables2/bootstrap.html"
        fields = ("id", "first_name", "last_name", "membership", "status", "registrationDate", "expirationDate", "receipt", "reference_number", "verificationID")

class UserMembershipTable(MembershipTable):
    class Meta(MembershipTable.Meta):
        exclude = ("actions", "first_name" ,"last_name")

class EventTable(tables.Table):
    record = tables.TemplateColumn(template_name='papsas_app/partial_list/event_record_column.html', orderable=False)
    actions = tables.TemplateColumn(template_name='papsas_app/partial_list/event_action_column.html', orderable=False)
    eventName = tables.Column(orderable=True, verbose_name="Name")
    startDate = tables.Column(orderable=True, verbose_name="Start Date")
    endDate = tables.Column(orderable=True, verbose_name="End Date")
    average_rating = tables.Column(orderable=True, verbose_name="Average Rating")

    def render_average_rating(self, record):
        return record.average_rating()
    
    class Meta:
        model = Event
        template_name = "django_tables2/bootstrap.html"
        fields = ("id", "eventName", "startDate", "endDate", "record", "exclusive", "average_rating", "actions")

class EventRegistrationTable(tables.Table):
    user = tables.Column(orderable = True, verbose_name="User")
    actions = tables.TemplateColumn(template_name='papsas_app/partial_list/event_reg_action_column.html', orderable = False)

    def render_user(self, record):
         return f'{record.user.first_name} {record.user.last_name}'
    
    class Meta:
        model = EventRegistration
        fields = ('id', 'user', 'reference_number', 'registered_at', 'status', 'actions')
        template_name = "django_tables2/bootstrap4.html"

class UserEventRegistrationTable(EventRegistrationTable):
    class Meta(EventRegistrationTable.Meta):
        exclude = ("actions", "user")

class EventAttendanceTable(tables.Table):
    event = tables.Column(accessor='event.event.eventName', verbose_name='Event Name')

    def render_user(self, record):
        return f'{record.user.first_name} {record.user.last_name}'

    class Meta:
        model = Attendance
        fields = ('id', 'event', 'user', 'attended', 'date_attended')
        template_name = "django_tables2/bootstrap4.html"
    
class UserEventAttendanceTable(EventAttendanceTable):
    class Meta(EventAttendanceTable.Meta):
        exclude = ("actions", "user")
    

class VenueTable(tables.Table):
    actions = tables.TemplateColumn(template_name='papsas_app/partial_list/venue_action_column.html')
    
    class Meta:
        model = Venue
        fiels = ('id' , 'name', 'address', 'capacity')
        template_name = "django_tables2/bootstrap.html"

class AchievementTable(tables.Table):
    actions = tables.TemplateColumn(template_name='papsas_app/partial_list/achievement_action_column.html')
    def render_pubmat(self, record):
        return format_html('<img src="{}" width="50" height="50">', record.pubmat.url)
    
    def render_description(self, value):
        if len(value) > 100:
            return f'{value[:100]}...'
        return value
    
    class Meta:
        model = Achievement
        fields = ('id', 'name', 'description', 'postStamp', 'pubmat')

class NewsAndOfferTable(tables.Table):
    actions = tables.TemplateColumn(template_name='papsas_app/partial_list/news_offers_action_column.html')

    def render_pubmat(self, record):
        return format_html('<img src="{}" width="50" height="50">', record.pubmat.url)
    
    def render_description(self, value):
        if len(value) > 100:
            return f'{value[:100]}...'
        return value
    
    class Meta:
        model = NewsandOffers
        fields = ('id', 'name', 'description', 'postStamp', 'pubmat')

class ElectionTable(tables.Table):
    startDate = tables.Column(orderable= True, verbose_name= "Opening Date")
    endDate = tables.Column(orderable= True, verbose_name= "Closing Date")
    numWinners = tables.Column(orderable= True, verbose_name="Officer Spot/s")
    

    def render_title(self, record):
        url = reverse('election_table', args=[record.id])
        return format_html('<a href="{}">{}<a>', url, record.title)

    class Meta:
        model = Election
        fields = ('id', 'title', 'startDate', 'endDate', 'numWinners')

class VoteTable(tables.Table):
    candidate = tables.Column(accessor='candidate', verbose_name='Candidate')
    election = tables.Column(accessor='election.title', verbose_name='Election')
    vote_count = tables.Column(accessor='vote_count', verbose_name='Vote Count')

    class Meta:
        model = Candidacy
        template_name = "django_tables2/bootstrap.html"
        fields = ("id" ,"candidate", "election", "vote_count")

    def render_candidate(self, value):
        return f"{value.first_name} {value.last_name}"

    def render_vote_count(self, value):
        return value or 0