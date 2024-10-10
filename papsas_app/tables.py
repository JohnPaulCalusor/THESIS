import django_tables2 as tables
from django.utils.html import format_html
from .models import User, UserMembership, Event, EventRegistration, Attendance, Achievement, NewsandOffers
from django.urls import reverse
from django.utils.safestring import mark_safe

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
    actions = tables.TemplateColumn(template_name='papsas_app/partial_list/membership_action_column.html', orderable=False, verbose_name='Actions')
    first_name = tables.Column(accessor='user.first_name', verbose_name='First Name')
    last_name = tables.Column(accessor='user.last_name', verbose_name='Last Name')
    registrationDate = tables.Column(orderable=True, verbose_name="Registration Date")
    expirationDate = tables.Column(orderable=True, verbose_name="Expiration Date")
    verificationID = tables.Column(orderable=True, verbose_name="Verification Id")
    membershipVerification = tables.Column(orderable=True, verbose_name="Status")

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
        fields = ("id", "first_name", "last_name", "membership", "membershipVerification", "registrationDate", "expirationDate", "receipt", "reference_number", "verificationID")

class EventTable(tables.Table):
     record = tables.TemplateColumn(template_name='papsas_app/partial_list/event_record_column.html', orderable = False)
     actions = tables.TemplateColumn(template_name='papsas_app/partial_list/event_action_column.html', orderable = False)
     eventName = tables.Column(orderable=True, verbose_name="Name")
     startDate = tables.Column(orderable=True, verbose_name="Start Date")
     endDate = tables.Column(orderable=True, verbose_name="End Date")
     
     class Meta:
          model = Event
          template_name = "django_tables2/bootstrap.html"
          fields = ("id", "eventName", "startDate", "endDate")

class EventRegistrationTable(tables.Table):
    user = tables.Column(orderable = True, verbose_name="User")
    actions = tables.TemplateColumn(template_name='papsas_app/partial_list/event_reg_action_column.html', orderable = False)

    def render_user(self, record):
         return f'{record.user.first_name} {record.user.last_name}'
    
    class Meta:
        model = EventRegistration
        fields = ('id', 'user', 'reference_number', 'registered_at', 'status', 'actions')
        template_name = "django_tables2/bootstrap4.html"

class EventAttendanceTable(tables.Table):
    event = tables.Column(accessor='event.event.eventName', verbose_name='Event Name')

    def render_user(self, record):
        return f'{record.user.first_name} {record.user.last_name}'

    class Meta:
        model = Attendance
        fields = ('id', 'event', 'user', 'attended', 'date_attended')
        template_name = "django_tables2/bootstrap4.html"
    

    