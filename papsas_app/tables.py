import django_tables2 as tables
from django.utils.html import format_html
from .models import User, UserMembership
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
    verificationID = tables.Column(orderable=False, verbose_name="Verification Id")
    membershipVerification = tables.Column(orderable=True, verbose_name="Status")

    def render_verificationID(self, record):
        return format_html('<img src="{}" width="50" height="50">', record.verificationID.url)
    
    def render_receipt(self, record):
        return format_html('<img src="{}" width="50" height="50">', record.receipt.url)
    
    class Meta:
        model = UserMembership
        template_name = "django_tables2/bootstrap.html"
        fields = ("id", "first_name", "last_name", "membership", "membershipVerification", "registrationDate", "expirationDate", "receipt", "reference_number", "verificationID")
