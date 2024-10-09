import django_tables2 as tables
from django.utils.html import format_html
from .models import User, UserMembership
from django.urls import reverse
from django.utils.safestring import mark_safe

class UserTable(tables.Table):
    actions = tables.Column(empty_values=(), orderable=False)
    profilePic = tables.Column(orderable=False, verbose_name="Profile Picture")

    def render_actions(self, record):
        update_button = format_html(
            '<a class="btn btn-primary btn-sm update-button" data-user-id="{}">Update</a>',
            record.id
        )
        
        delete_form = format_html('''
            <form action="{}" method="post">
                <button class="btn btn-danger btn-sm" title="Deactivate" type="submit">
                    Deactivate
                </button>
            </form>
        ''', reverse('delete_account', args=[record.id]))

        return mark_safe(f'{update_button}&nbsp;{delete_form}')

    def render_profilePic(self, record):
            return format_html('<img src="{}" width="50" height="50">', record.profilePic.url)
    
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
